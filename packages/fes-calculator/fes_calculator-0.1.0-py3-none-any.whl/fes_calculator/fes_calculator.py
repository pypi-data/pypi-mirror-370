import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy import interpolate
try:
    from mpi4py import MPI
except ImportError:
    print("Warning: mpi4py not found. MPI parallelization will be disabled.")
    # Create a dummy MPI object if mpi4py is not installed
    class DummyComm:
        def Get_rank(self): return 0
        def Get_size(self): return 1
        def bcast(self, obj, root=0): return obj
        def scatter(self, sendobj, root=0): return sendobj[0]
        def gather(self, sendobj, root=0): return [sendobj]

    class DummyMPI:
        COMM_WORLD = DummyComm()

    MPI = DummyMPI()


class FES_calculator:
    """
    A class to calculate Free Energy Surfaces (FES) from molecular dynamics simulations,
    with support for metadynamics reweighting and MPI parallelization for vbias calculation.
    """
    def __init__(self, T0, T, biasf, tmin, tmax, w_cv, w_hill, sigma,
                 gridmin_list, gridmax_list, griddiff_list, nbin_list, periodic_cv_flags,plot_fesmin,plot_fesmax):
        self.T0 = T0
        self.T = T
        self.biasf = biasf
        self.tmin = tmin
        self.tmax = tmax
        self.w_cv = w_cv
        self.w_hill = w_hill
        
        if not isinstance(sigma, list):
            raise TypeError("'sigma' must be a list of floats or None.")
        if len(sigma) != len(gridmin_list):
            raise ValueError("Length of 'sigma' list must match the number of CVs.")
        self.sigma = sigma

        self.gridmin_list = gridmin_list
        self.gridmax_list = gridmax_list
        self.griddiff_list = griddiff_list
        self.nbin_list = nbin_list
        self.periodic_cv_flags = periodic_cv_flags
        self.plot_fesmin=plot_fesmin
        self.plot_fesmax=plot_fesmax

        if len(self.periodic_cv_flags) != len(self.gridmin_list):
            raise ValueError("Length of 'periodic_cv_flags' must match the number of CVs.")

        self.KB = 1.9872041e-3  # Boltzmann constant in kcal/(mol*K)
        self.kt = self.KB * self.T
        self.beta_sys = 1.0 / self.kt
        self.alpha = (self.T + (self.biasf - 1) * self.T) / ((self.biasf - 1) * self.T) if (self.biasf - 1) * self.T != 0 else 1.0

    def _read_colvar(self, filename, column_indices_to_read=None):
        try:
            data = np.loadtxt(filename)
            all_cvs = data[:, 1::2] 
            if column_indices_to_read is None:
                column_indices_to_read = list(range(all_cvs.shape[1]))
            if any(i >= all_cvs.shape[1] for i in column_indices_to_read):
                print(f"Error: Column index out of bounds for COLVAR file with {all_cvs.shape[1]} CVs.")
                return None
            return [all_cvs[:, i] for i in column_indices_to_read]
        except (FileNotFoundError, Exception) as e:
            print(f"Error reading COLVAR file '{filename}': {e}")
            return None

    def _read_hills(self, filename, column_indices_to_read=None):
        try:
            data = np.loadtxt(filename)
            hill_coords_all = data[:, 1:-2:2]
            if column_indices_to_read is None:
                column_indices_to_read = list(range(hill_coords_all.shape[1]))
            if any(i >= hill_coords_all.shape[1] for i in column_indices_to_read):
                print(f"Error: Column index out of bounds for HILLS file with {hill_coords_all.shape[1]} biased CVs.")
                return None, None
            selected_hills = [hill_coords_all[:, i] for i in column_indices_to_read]
            height = data[:, -2] * 0.239006 # Convert kJ/mol to kcal/mol
            return selected_hills, height
        except (FileNotFoundError, Exception) as e:
            print(f"Error reading HILLS file '{filename}': {e}")
            return None, None

    def _read_vbias_ct_files(self, vbias_file, ct_file):
        vbias_data, ct_data = None, None
        try:
            vbias_data = np.loadtxt(vbias_file)[:, 1]
        except (FileNotFoundError, IndexError) as e:
            print(f"Error processing vbias file '{vbias_file}': {e}")
        try:
            ct_data = np.loadtxt(ct_file)[:, 1]
        except (FileNotFoundError, IndexError) as e:
            print(f"Error processing CT file '{ct_file}': {e}")
        return vbias_data, ct_data

    def _compute_vbias_segment(self, cv_segments, hill_coords, height, alpha, effective_cv_indices, rank_for_tqdm=0):
        if not cv_segments or not cv_segments[0].size > 0:
            return np.array([])
        nsteps, num_cvs = len(cv_segments[0]), len(cv_segments)
        vbias = np.zeros(nsteps)
        iterator = tqdm(range(nsteps), desc=f"Calculating vbias (rank {rank_for_tqdm})", disable=(rank_for_tqdm != 0))
        for i_local in iterator:
            mtd_max = int((i_local + 1) * self.w_cv / self.w_hill)
            if mtd_max == 0 or not hill_coords or not hill_coords[0].size > 0:
                continue
            mtd_max = min(mtd_max, len(hill_coords[0]))
            total_exponent = np.zeros(mtd_max, dtype=np.float64)
            for j in range(num_cvs):
                original_cv_index = effective_cv_indices[j]
                sigma_val = self.sigma[original_cv_index]
                if sigma_val is None or sigma_val <= 0: continue
                dsq = sigma_val ** 2
                diff = cv_segments[j][i_local] - hill_coords[j][:mtd_max]
                if self.periodic_cv_flags[original_cv_index]:
                    pmin, pmax = self.gridmin_list[original_cv_index], self.gridmax_list[original_cv_index]
                    L, half_L = pmax - pmin, (pmax - pmin) / 2.0
                    diff = np.where(diff > half_L, diff - L, diff)
                    diff = np.where(diff < -half_L, diff + L, diff)
                total_exponent += (diff ** 2) / (2.0 * dsq)
            e = np.exp(-total_exponent)
            vbias[i_local] = np.sum((height[:mtd_max] / alpha) * e)
        return vbias

    def calculate_vbias(self, colvar_file, hills_file, output_file="vbias.dat", column_indices_to_read=None):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        data_to_scatter = None
        selected_hills = None
        height = None
        effective_cv_indices = None
        if rank == 0:
            print(f"Starting parallel vbias calculation on {size} cores to {output_file}...")
            selected_cvs_all = self._read_colvar(colvar_file, column_indices_to_read)
            selected_hills, height = self._read_hills(hills_file, column_indices_to_read)
            if selected_cvs_all is None or selected_hills is None:
                print("Aborting vbias calculation due to input file errors.")
                comm.bcast(None, root=0)
                return
            effective_cv_indices = column_indices_to_read if column_indices_to_read is not None else list(range(len(selected_hills)))
            for cv_index in effective_cv_indices:
                if self.sigma[cv_index] is None:
                    print(f"Error: vbias requested for CV {cv_index}, but its sigma is None. Aborting.")
                    comm.bcast(None, root=0)
                    return
            cv_segments_split = [np.array_split(cv_data, size) for cv_data in selected_cvs_all]
            data_to_scatter = [list(item) for item in zip(*cv_segments_split)]
        selected_hills = comm.bcast(selected_hills, root=0)
        if selected_hills is None: return
        height = comm.bcast(height, root=0)
        effective_cv_indices = comm.bcast(effective_cv_indices, root=0)
        cv_segments_local = comm.scatter(data_to_scatter, root=0)
        vbias_local = self._compute_vbias_segment(cv_segments_local, selected_hills, height, self.alpha, effective_cv_indices, rank_for_tqdm=rank)
        vbias_chunks = comm.gather(vbias_local, root=0)
        if rank == 0:
            full_vbias = np.concatenate(vbias_chunks)
            try:
                with open(output_file, 'w') as f:
                    for i, val in enumerate(full_vbias, 1):
                        f.write(f"{i:10d} {val:16.8f}\n")
                print(f"vbias written to {output_file}")
            except IOError as e:
                print(f"Error writing vbias data to file {output_file}: {e}")

    def compute_ct_values(self, hill_coords, height, nbins, gridmins, griddiffs, effective_cv_indices):
        num_hills = len(hill_coords[0]) if hill_coords and hill_coords[0].size > 0 else 0
        if num_hills == 0:
            print("No hills data to compute CT values."); return np.array([])
        num_cvs = len(hill_coords)
        ct_values = np.zeros(num_hills)
        kT_biased = self.kt * self.biasf
        grids = [gridmins[i] + griddiffs[i] * np.arange(nbins[i]) for i in range(num_cvs)]
        mesh = np.meshgrid(*grids, indexing='ij')
        flat_mesh = [X.ravel() for X in mesh]
        total_bias_potential = np.zeros_like(flat_mesh[0], dtype=np.float64)
        for i_mtd in tqdm(range(num_hills), desc="Computing CT"):
            h_hill = height[i_mtd]
            total_exponent = np.zeros_like(flat_mesh[0], dtype=np.float64)
            for j in range(num_cvs):
                original_cv_index = effective_cv_indices[j]
                sigma_val = self.sigma[original_cv_index]
                if sigma_val is None or sigma_val <= 0: continue
                dsq = sigma_val ** 2
                s_hill = hill_coords[j][i_mtd]
                diff = flat_mesh[j] - s_hill
                if self.periodic_cv_flags[original_cv_index]:
                    pmin, pmax = self.gridmin_list[original_cv_index], self.gridmax_list[original_cv_index]
                    L, half_L = pmax - pmin, (pmax - pmin) / 2.0
                    diff = np.where(diff > half_L, diff - L, diff)
                    diff = np.where(diff < -half_L, diff + L, diff)
                total_exponent += (diff**2) / (2.0 * dsq)
            current_hill_bias_contribution = -h_hill * np.exp(-total_exponent)
            total_bias_potential += current_hill_bias_contribution
            numerator = np.sum(np.exp(-total_bias_potential / self.kt))
            denominator = np.sum(np.exp(-total_bias_potential / kT_biased))
            ct_values[i_mtd] = self.kt * np.log(numerator / denominator) if denominator != 0 else 0.0
        return ct_values

    def calculate_ct(self, hills_file, output_file="ct.dat", column_indices_to_read=None):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank != 0:
            return
        print(f"Starting CT calculation to {output_file}...")
        selected_hills, height = self._read_hills(hills_file, column_indices_to_read)
        if selected_hills is None or height is None:
            print("Aborting CT calculation due to HILLS file errors."); return
        effective_cv_indices = column_indices_to_read if column_indices_to_read is not None else list(range(len(selected_hills)))
        for cv_index in effective_cv_indices:
            if self.sigma[cv_index] is None:
                print(f"Error: CT calculation requested for CV {cv_index}, but its sigma is None. Aborting."); return
        griddiffs = [self.griddiff_list[i] for i in effective_cv_indices]
        nbins = [self.nbin_list[i] for i in effective_cv_indices]
        gridmins = [self.gridmin_list[i] for i in effective_cv_indices]
        ct_values = self.compute_ct_values(selected_hills, height, nbins, gridmins, griddiffs, effective_cv_indices)
        try:
            with open(output_file, 'w') as f:
                for i, val in enumerate(ct_values, 1):
                    f.write(f"{i:10d} {val:16.8f}\n")
            print(f"CT values written to {output_file}")
        except IOError as e:
            print(f"Error writing CT data to file {output_file}: {e}")

    def calculate_fes(self, colvar_file, column_indices_to_read, projection_pairs, 
                      vbias_file=None, ct_file=None, plot=False, use_mtd=False):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank != 0:
            return
        print(f"Starting FES calculation (Metadynamics reweighting: {'Enabled' if use_mtd else 'Disabled'})...")
        selected_cvs = self._read_colvar(colvar_file, column_indices_to_read)
        if selected_cvs is None:
            print("Aborting FES calculation due to COLVAR file error."); return
        vbias_data, ct_data = np.array([]), np.array([])
        if use_mtd:
            if vbias_file and ct_file:
                vbias_data, ct_data = self._read_vbias_ct_files(vbias_file, ct_file)
                if vbias_data is None or ct_data is None:
                    print("Aborting FES calculation due to vbias/ct file error."); return
            else:
                print("Error: use_mtd is True, but vbias_file or ct_file not provided."); return
        original_cv_indices = column_indices_to_read if column_indices_to_read is not None else list(range(len(selected_cvs)))
        selected_grid_params = [(self.gridmin_list[i], self.griddiff_list[i], self.nbin_list[i]) for i in original_cv_indices]
        fes_projections = self._calculate_probability_and_fes(
            selected_cvs, vbias_data, ct_data, selected_grid_params, 
            projection_pairs, original_cv_indices, use_mtd=use_mtd
        )
        if fes_projections:
            output_files = self._write_fes_projections(fes_projections, original_cv_indices)
            if plot and output_files:
                for f in output_files: self.plot_fes(f)


    def _calculate_probability_and_fes(self, selected_cvs, vbias_data, ct_data, selected_grid_params, 
                                      projection_pairs, original_cv_indices, use_mtd=True):
        num_cvs = len(selected_cvs)
        prob_shape = tuple(p[2] for p in selected_grid_params)
        prob_nd = np.zeros(prob_shape, dtype=np.float64)
        md_steps_total = len(selected_cvs[0])
        print("Calculating probability distribution...")
        for i_md in tqdm(range(md_steps_total)):
            current_md_step = i_md + 1
            if not (self.tmin <= current_md_step <= self.tmax): continue
            indices_list = []
            all_indices_valid = True
            for j in range(num_cvs):
                cv_val = selected_cvs[j][i_md]
                gridmin, griddiff, nbin = selected_grid_params[j]
                original_index = original_cv_indices[j]
                index = int(round((cv_val - gridmin) / griddiff))
                if self.periodic_cv_flags[original_index]:
                    index = index % nbin
                elif not (0 <= index < nbin):
                    all_indices_valid = False
                    break
                indices_list.append(index)
            if not all_indices_valid: continue
            weight = 1.0
            if use_mtd:
                i_mtd_idx = int(current_md_step * self.w_cv / self.w_hill) - 1
                if 0 <= i_mtd_idx < len(ct_data) and i_md < len(vbias_data):
                    dum_val = vbias_data[i_md] - ct_data[i_mtd_idx]
                    weight = np.exp(dum_val / self.kt)
            prob_nd[tuple(indices_list)] += weight
        fes_projections = {}
        print("Calculating FES projections...")
        for ix, iy in projection_pairs:
            sum_axes = tuple(k for k in range(num_cvs) if k not in (ix, iy))
            prob_2d = np.sum(prob_nd, axis=sum_axes)
            fes_2d = np.full_like(prob_2d, np.inf, dtype=np.float64)
            non_zero_mask = prob_2d > 1e-30
            prob_sum = np.sum(prob_2d[non_zero_mask])
            if prob_sum > 0:
                normalized_prob = prob_2d[non_zero_mask] / prob_sum
                fes_2d[non_zero_mask] = -self.kt * np.log(normalized_prob)
            grid_x = selected_grid_params[ix][0] + selected_grid_params[ix][1] * np.arange(selected_grid_params[ix][2])
            grid_y = selected_grid_params[iy][0] + selected_grid_params[iy][1] * np.arange(selected_grid_params[iy][2])
            fes_projections[(ix, iy)] = (grid_x, grid_y, fes_2d)
        return fes_projections

    def read_and_process_replicas_TASS(self, replica_input_file, column_indices_to_read, num_replicas, plot=False):
        """
        Reads replica data, applies periodic boundary conditions based on CV flags, 
        calculates forces, and computes 2D FES using the TASS approach.
        """
        kj_to_kcal = 0.239006
        cv1_list, cv2_list, dfds_list = [], [], []
        vbias_data_list, ct_data_list = [], []
        filenames_colvar_all, filenames_vbias_all, filenames_ct_all = [], [], []
        pcons_all, kcons_all = [], []

        # --- Phase 1: Read input files and prepare data ---
        try:
            with open(replica_input_file, 'r') as f:
                for i in range(num_replicas):
                    line1 = next(f).strip().split()
                    pcon, kcon_kj = map(float, line1)
                    filename_colvar = next(f).strip()
                    next(f) # Skip MTD file line
                    filename_vbias = next(f).strip()
                    filename_ct = next(f).strip()
                    
                    pcons_all.append(pcon)
                    kcons_all.append(kcon_kj * kj_to_kcal)
                    filenames_colvar_all.append(filename_colvar)
                    filenames_vbias_all.append(filename_vbias)
                    filenames_ct_all.append(filename_ct)
        except (StopIteration, IndexError, ValueError, FileNotFoundError) as e:
            print(f"Error reading or parsing '{replica_input_file}': {e}.")
            return tuple([np.array([])] * 7)

        num_replicas_read = len(filenames_colvar_all)
        if num_replicas_read == 0:
            print("Warning: No replica data parsed.")
            return tuple([np.array([])] * 7)

        # Get original indices for the two CVs being analyzed
        cv1_orig_idx, cv2_orig_idx = column_indices_to_read[0], column_indices_to_read[1]
        
        # Load data for all replicas
        for ir in range(num_replicas_read):
            selected_cvs = self._read_colvar(filenames_colvar_all[ir], column_indices_to_read)
            vbias_data, ct_data = self._read_vbias_ct_files(filenames_vbias_all[ir], filenames_ct_all[ir])

            if selected_cvs and len(selected_cvs) >= 2 and vbias_data is not None and ct_data is not None:
                cv1, cv2 = selected_cvs[0], selected_cvs[1]
                
                # Apply periodic boundary conditions based on flags for each CV
                if self.periodic_cv_flags[cv1_orig_idx]:
                    dmin, dmax = self.gridmin_list[cv1_orig_idx], self.gridmax_list[cv1_orig_idx]
                    drange = dmax - dmin
                    cv1 = np.where(cv1 > dmax, cv1 - drange, np.where(cv1 < dmin, cv1 + drange, cv1))
                if self.periodic_cv_flags[cv2_orig_idx]:
                    dmin, dmax = self.gridmin_list[cv2_orig_idx], self.gridmax_list[cv2_orig_idx]
                    drange = dmax - dmin
                    cv2 = np.where(cv2 > dmax, cv2 - drange, np.where(cv2 < dmin, cv2 + drange, cv2))
                
                cv1_list.append(cv1)
                cv2_list.append(cv2)

                diff_s = cv1 - pcons_all[ir]
                if self.periodic_cv_flags[cv1_orig_idx]:
                    dmin, dmax = self.gridmin_list[cv1_orig_idx], self.gridmax_list[cv1_orig_idx]
                    drange = dmax - dmin
                    dfds_list.append(-np.where(diff_s > drange/2, diff_s - drange, np.where(diff_s < -drange/2, diff_s + drange, diff_s)) * kcons_all[ir])
                else:
                    dfds_list.append(-diff_s * kcons_all[ir])
                
                vbias_data_list.append(vbias_data)
                ct_data_list.append(ct_data)
            else:
                print(f"  --> Skipping replica {ir+1} due to read error or insufficient data.")
                # Append empty arrays to maintain index consistency
                cv1_list.append(np.array([])); cv2_list.append(np.array([])); dfds_list.append(np.array([]))
                vbias_data_list.append(np.array([])); ct_data_list.append(np.array([]))

        # Pad arrays to uniform length
        max_md_steps = max((len(arr) for arr in cv1_list if arr.size > 0), default=0)
        max_ct_steps = max((len(arr) for arr in ct_data_list if arr.size > 0), default=0)
        
        cv1_all = np.full((num_replicas_read, max_md_steps), np.nan); cv2_all = np.full((num_replicas_read, max_md_steps), np.nan)
        dfds_all = np.full((num_replicas_read, max_md_steps), np.nan); vbias_all = np.full((num_replicas_read, max_md_steps), np.nan)
        ct_all = np.full((num_replicas_read, max_ct_steps), np.nan)

        for i in range(num_replicas_read):
            if cv1_list[i].size > 0:
                steps = len(cv1_list[i])
                cv1_all[i, :steps] = cv1_list[i]; cv2_all[i, :steps] = cv2_list[i]
                dfds_all[i, :steps] = dfds_list[i]
                vbias_all[i, :min(steps, len(vbias_data_list[i]))] = vbias_data_list[i][:min(steps, len(vbias_data_list[i]))]
            if ct_data_list[i].size > 0:
                ct_all[i, :len(ct_data_list[i])] = ct_data_list[i]
        
        # --- Phase 2: Calculate av_dfds1 and fes1 ---
        av_dfds1 = np.zeros(num_replicas_read)
        for ir in range(num_replicas_read):
            den, num = 0.0, 0.0
            t_max_md = min(self.tmax, dfds_all.shape[1]) 
            for i_md in range(self.tmin -1, t_max_md): # Adjust for 0-based indexing
                if np.isnan(vbias_all[ir, i_md]) or np.isnan(dfds_all[ir, i_md]): continue

                i_mtd = int((i_md + 1) * self.w_cv / self.w_hill) -1 # 0-based index
                
                if i_mtd < 0 or i_mtd >= ct_all.shape[1] or np.isnan(ct_all[ir, i_mtd]):
                    term_exp = 1.0 
                else:
                    dum = vbias_all[ir, i_md] - ct_all[ir, i_mtd]
                    term_exp = np.exp(dum / self.kt)
                
                num += dfds_all[ir, i_md] * term_exp
                den += term_exp
            
            av_dfds1[ir] = num / den if den != 0 else 0.0

        print('av_dfds1 computed.')
        np.savetxt("av_dfds.dat", np.column_stack((pcons_all, av_dfds1)), fmt='%.6f', header='pcons av_dfds1')
        
        fes1_replica = np.zeros(num_replicas_read)
        current_sum = 0.0
        for ir in range(num_replicas_read - 1):
            if np.isnan(av_dfds1[ir]) or np.isnan(av_dfds1[ir+1]):
                fes1_replica[ir+1] = np.nan
                continue
            dum = pcons_all[ir+1] - pcons_all[ir]
            current_sum += dum * (av_dfds1[ir+1] + av_dfds1[ir])
            fes1_replica[ir+1] = current_sum * 0.5
            
        print('fes1 computed.')
        np.savetxt("free_energy_1.dat", np.column_stack((pcons_all, fes1_replica)), fmt='%.6f', header='pcons fes1')
        
        # --- Phase 3: Calculate 2D Probability and FES ---
        print("\nCalculating 2D probability and FES...")
        gridmin1, gridmin2 = self.gridmin_list[cv1_orig_idx], self.gridmin_list[cv2_orig_idx]
        griddif1, griddif2 = self.griddiff_list[cv1_orig_idx], self.griddiff_list[cv2_orig_idx]
        nbin1, nbin2 = self.nbin_list[cv1_orig_idx], self.nbin_list[cv2_orig_idx]

        prob = np.zeros((nbin1, nbin2))
        norm = np.zeros(num_replicas_read)

        for ir in range(num_replicas_read):
            local_den = 0.0
            t_max_cv = min(self.tmax, cv1_all.shape[1])
            for i_md in range(self.tmin - 1, t_max_cv):
                if np.isnan(cv1_all[ir, i_md]) or np.isnan(cv2_all[ir, i_md]): continue

                index1 = int(round((cv1_all[ir, i_md] - gridmin1) / griddif1))
                index2 = int(round((cv2_all[ir, i_md] - gridmin2) / griddif2))
                
            
#                if self.periodic_cv_flags[cv1_orig_idx]:
#                    index1 = int(round((cv1 - gridmin1) / griddif1)) % nbin1
#                else:
#                    index1 = int(round((cv1 - gridmin1) / griddif1))
#            
#                if self.periodic_cv_flags[cv2_orig_idx]:
#                    index2 = int(round((cv2 - gridmin2) / griddif2)) % nbin2
#                else:
#                    index2 = int(round((cv2 - gridmin2) / griddif2))

            # Check if non-periodic indices are within bounds
#                if (not self.periodic_cv_flags[cv1_orig_idx] and not (0 <= index1 < nbin1)) or \
#                    (not self.periodic_cv_flags[cv2_orig_idx] and not (0 <= index2 < nbin2)):
#                    continue



                i_mtd = int((i_md + 1) * self.w_cv / self.w_hill) - 1

                if 0 <= index1 < nbin1 and 0 <= index2 < nbin2:
                    weight = 1.0
                    if i_mtd >= 0 and i_mtd < ct_all.shape[1] and not np.isnan(ct_all[ir, i_mtd]):
                        dum = vbias_all[ir, i_md] - ct_all[ir, i_mtd]
                        weight = np.exp(dum / self.kt)
                    
                    prob[index1, index2] += weight
                    local_den += weight

            norm[ir] = 1.0 / (local_den * griddif1 * griddif2) if local_den != 0 else 0.0

        print('prob computed')
        
        # --- Phase 4: Compute 2D FES ---
        s1 = np.linspace(gridmin1, gridmin1 + (nbin1 - 1) * griddif1, nbin1)
        s2 = np.linspace(gridmin2, gridmin2 + (nbin2 - 1) * griddif2, nbin2)
        
        fes1_grid = np.zeros_like(s1)
        if num_replicas_read > 1:
            valid_pcons = np.array(pcons_all)[~np.isnan(fes1_replica)]
            valid_fes1 = fes1_replica[~np.isnan(fes1_replica)]
            if len(valid_pcons) > 1:
                fes1_interp_func = interpolate.interp1d(valid_pcons, valid_fes1, kind='linear', fill_value='extrapolate')
                fes1_grid = fes1_interp_func(s1)
        
        fes = np.zeros((nbin1, nbin2))
        for i_s1 in range(nbin1):
            for i_s2 in range(nbin2):
                current_norm_factor = norm[i_s1] if i_s1 < num_replicas_read else 1.0
                num_val = prob[i_s1, i_s2] * current_norm_factor
                fes[i_s1, i_s2] = -self.kt * np.log(np.maximum(num_val, 1E-32)) + fes1_grid[i_s1]
                
        print('2D FES computed.')

        fes_projections_dict = {(0, 1): (s1, s2, fes)}
        output_files = self._write_fes_projections(fes_projections_dict, column_indices_to_read)
        if plot and output_files:
            for f in output_files: self.plot_fes(f)

        return cv1_all, cv2_all, dfds_all, av_dfds1, fes1_replica, prob, fes

    def compute_TASS(self, replica_input_filename, num_replicas, column_indices_to_read, plot=False):
        """
        Orchestrates the TASS simulation data processing.
        """
        print(f"Starting TASS calculation with {num_replicas} replicas...")
        return self.read_and_process_replicas_TASS(
            replica_input_filename, column_indices_to_read, num_replicas, plot=plot
        )

    def _write_fes_projections(self, fes_projections, original_cv_indices):
        output_files = []
        for (ix, iy), (grid_x, grid_y, fes_2d) in fes_projections.items():
            orig_ix, orig_iy = original_cv_indices[ix], original_cv_indices[iy]
            filename = f"FES_projection_cv{orig_ix}-cv{orig_iy}.dat"
            output_files.append(filename)
            print(f"Writing FES projection to {filename}...")
            try:
                with open(filename, "w") as f:
                    f.write(f"# FES Projection for original CV {orig_ix} vs CV {orig_iy}\n")
                    f.write("# Col 1: CV Value (X), Col 2: CV Value (Y), Col 3: Free Energy (kcal/mol)\n")
                    for i in range(len(grid_x)):
                        for j in range(len(grid_y)):
                            f.write(f"{grid_x[i]:16.8E} {grid_y[j]:16.8E} {fes_2d[i, j]:16.8E}\n")
                        f.write("\n")
            except IOError as e:
                print(f"Error writing FES projection to file {filename}: {e}")
        return output_files

    def plot_fes(self, filename):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank != 0:
            return
        try:
            print(f"Plotting {filename}...")
            data = np.loadtxt(filename)
            x, y, z = data[:, 0], data[:, 1], data[:, 2]
            finite_z = z[np.isfinite(z)]
            if len(finite_z) == 0:
                print(f"Warning: No finite FES values in {filename}. Skipping plot."); return
            z_shifted = z - np.min(finite_z)
            nx, ny = len(np.unique(x)), len(np.unique(y))
            X, Y, Z = x.reshape((ny, nx)).T, y.reshape((ny, nx)).T, z_shifted.reshape((ny, nx)).T
            fig, ax = plt.subplots(figsize=(8, 7))
            fesmin=self.plot_fesmin
            fesmax=self.plot_fesmax
            levels = np.arange(0, 21, 1)
            c = ax.contourf(X, Y, Z, levels=np.arange(fesmin, fesmax, 1), cmap='Spectral_r', extend='max')
            ax.contour(X, Y, Z, levels=np.arange(fesmin, fesmax, 2), colors='black', linewidths=0.5)
#            c = ax.contourf(X, Y, Z, levels=levels, cmap='viridis_r', extend='max')
#            ax.contour(X, Y, Z, levels=np.arange(0, 21, 2), colors='white', linewidths=0.5, alpha=0.7)
            cv_indices_str = filename.split("_cv")[1].split(".dat")[0]
            cv1_label, cv2_label = cv_indices_str.split("-")
            ax.set_xlabel(f'CV {cv1_label}', fontsize=16)
            ax.set_ylabel(f'CV {cv2_label}', fontsize=16)
            ax.tick_params(axis='both', which='major', labelsize=12)
            cb = fig.colorbar(c, ax=ax)
            cb.set_label("Free Energy (kcal/mol)", fontsize=14)
            plt.tight_layout()
            plt.savefig(filename.replace('.dat', '.png'))
            plt.show()
            plt.close(fig)
        except Exception as e:
            print(f"Could not plot FES from {filename}: {e}")


if __name__ == '__main__':
    # --- 1. DEFINE SIMULATION PARAMETERS ---
    T_val, biasf_val = 300.0, 10.0
    tmin_val, tmax_val = 1, 10000
    w_cv_val, w_hill_val = 1.0, 100.0
    sigma_val_list = [0.4, 0.5, None, None]
    gridmin_list_val = [-np.pi, -5.0, 0.0, 0.0]
    gridmax_list_val = [np.pi, 5.0, 1.0, 1.0]
    griddiff_list_val = [0.1, 0.2, 0.1, 0.1]
    nbin_list_val = [int(round((mx - mn) / df)) for mn, mx, df in zip(gridmin_list_val, gridmax_list_val, griddiff_list_val)]
    periodic_flags_val = [True, False, False, False] 

    # --- 2. CREATE DUMMY INPUT FILES (for demonstration) ---
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        print("Creating dummy input files for demonstration...")
        np.random.seed(42)
        num_steps = 10000
        time = np.arange(1, num_steps + 1)
        cv1_data = np.sin(np.linspace(0, 5 * np.pi, num_steps)) * 1.5
        cv2_data = np.linspace(-4, 4, num_steps) + np.random.normal(0, 0.5, num_steps)
        cv3_data = np.random.rand(num_steps)
        cv4_data = np.random.rand(num_steps)
        np.savetxt("COLVAR.dat", np.column_stack((time, 
            cv1_data, np.zeros(num_steps), cv2_data, np.zeros(num_steps),
            cv3_data, np.zeros(num_steps), cv4_data, np.zeros(num_steps))), fmt='%.4f')
        num_hills = int(num_steps / w_hill_val)
        hill_time = np.arange(1, num_hills + 1) * w_hill_val
        hill_cv1 = np.random.uniform(gridmin_list_val[0], gridmax_list_val[0], num_hills)
        hill_cv2 = np.random.uniform(gridmin_list_val[1], gridmax_list_val[1], num_hills)
        hill_height = np.full(num_hills, 1.0)
        np.savetxt("HILLS.dat", np.column_stack((
            hill_time, 
            hill_cv1, np.full(num_hills, sigma_val_list[0]), 
            hill_cv2, np.full(num_hills, sigma_val_list[1]), 
            hill_height, np.full(num_hills, 0.1))), fmt='%.4f')
    comm.Barrier()

    # --- 3. INITIALIZE THE CALCULATOR ---
    fes_calc = FES_calculator(T_val, T_val, biasf_val, tmin_val, tmax_val,
                             w_cv_val, w_hill_val, sigma_val_list,
                             gridmin_list_val, gridmax_list_val, griddiff_list_val, 
                             nbin_list_val, periodic_flags_val)

    # --- 4. RUN CALCULATIONS ---
    # Example 1: Calculate vbias in parallel for the two biased CVs
    fes_calc.calculate_vbias(
        colvar_file="COLVAR.dat", hills_file="HILLS.dat",
        output_file="vbias_parallel.dat", column_indices_to_read=[0, 1]
    )

    # Example 2: Calculate a 2D FES from a histogram (no reweighting)
    if rank == 0:
        print("\n--- Running FES calculation (histogram) on root process---")
        fes_calc.calculate_fes(
            colvar_file="COLVAR.dat", 
            column_indices_to_read=[0, 1],
            projection_pairs=[(0, 1)],
            plot=True, 
            use_mtd=False
        )
