import concurrent.futures
from time import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse


def quadric_proj(quadric, idx):
    """projects along one axis of the quadric"""

    # delete if orthogonal
    zero = 1e-8
    if np.abs(quadric[idx, idx]) < zero:
        return np.delete(np.delete(quadric, idx, axis=0), idx, axis=1)

    # row/column along which to perform the orthogonal projection
    vec = 0.5 * (quadric[idx, :] + quadric[:, idx])  # symmetrise if not symmetric
    vec /= np.sqrt(quadric[idx, idx])  # normalise to indexed component
    proj_op = np.outer(vec, vec)  # projection operator
    ortho_proj = quadric - proj_op  # projected quadric

    return np.delete(np.delete(ortho_proj, idx, axis=0), idx, axis=1)


def incoh_sigma(mat, axis):
    """Incoherent sigma"""
    idx = int(axis)

    for i in (3, 2, 1, 0):
        if not i == idx:
            mat = quadric_proj(mat, i)

    return 1 / np.sqrt(np.abs(mat[0, 0]))


def model_disp(vq1, vq2, vq3):
    """return energy for given Q points
    3d FM J=-1 meV S=1, en=6*S*J*(1-cos(Q))
    """

    sj = 1
    gamma_q = np.cos(2 * np.pi * vq1)
    # gamma_q = (np.cos(2 * np.pi * vq1) + np.cos(2 * np.pi * vq2) + np.cos(2 * np.pi * vq3)) / 3

    disp = 2 * sj * (1 - gamma_q)
    disp = np.array((disp - 2, disp + 2))

    # reshape if only one band
    num_disp = len(disp.shape)
    if num_disp == 1:
        disp = np.reshape(disp, (1, np.size(disp)))
    return disp


def model_inten(vq1, vq2, vq3):
    """return intensity for given Q points
    3d FM J=-1 meV S=1, inten = S/2 for all Qs
    """
    inten = np.ones_like(vq1, dtype=float) / 2
    inten = np.array((inten, inten))

    # reshape if only one band
    num_inten = len(inten.shape)
    if num_inten == 1:
        inten = np.reshape(inten, (1, np.size(inten)))

    return inten


def resolution_matrix(qx0, qy0, qz0, en0):
    """Fake resoltuion matrix mat and prefactor r0
    r0 is a constant, rez_mat is a symmatric positive 4 by 4 matrix
    """

    sz = np.shape(qx0)

    def rotation_matrix_4d(theta_deg):
        theta = np.radians(theta_deg)
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array(
            [
                [c, 0, 0, -s],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [s, 0, 0, c],
            ]
        )

    sigma1, sigma2 = 0.3, 0.02
    sigma3 = sigma4 = 1
    angle = -80
    mat = np.array(
        [
            [1 / sigma1**2, 0, 0, 0],
            [0, 1 / sigma3**2, 0, 0],
            [0, 0, 1 / sigma4**2, 0],
            [0, 0, 0, 1 / sigma2**2],
        ]
    )
    rez_mat = rotation_matrix_4d(angle).T @ mat @ rotation_matrix_4d(angle)
    r0 = 1
    return np.broadcast_to(r0, sz), np.broadcast_to(rez_mat, sz + (4, 4))


def plot_rez_ellipses(ax):
    sigma1, sigma2 = 0.3, 0.02
    angle = 80
    for i in range(3):
        ax.add_artist(
            Ellipse(
                xy=(0, 0),
                width=sigma1 * 2 * (i + 1),
                height=sigma2 * 2 * (i + 1),
                angle=angle,
                edgecolor="w",
                facecolor="none",
                label=f"{i + 1}-sigma",
            )
        )


def convolution(qh, qk, ql, en):
    # ----------------------------------------------------
    # calculate resolution matrix for all points
    # ----------------------------------------------------
    r0, mat = resolution_matrix(qh, qk, ql, en)
    mat_hkl = quadric_proj(mat, 3)
    # ----------------------------------------------------
    # calculate the incoherent sigmas for three Q directions
    # ----------------------------------------------------
    sigma_qh = incoh_sigma(mat, 0)
    sigma_qk = incoh_sigma(mat, 1)
    sigma_ql = incoh_sigma(mat, 2)
    sigma_en = incoh_sigma(mat, 3)

    num_of_sigmas = 3
    min_qh, max_qh = qh - num_of_sigmas * sigma_qh, qh + num_of_sigmas * sigma_qh
    min_qk, max_qk = qk - num_of_sigmas * sigma_qk, qk + num_of_sigmas * sigma_qk
    min_ql, max_ql = ql - num_of_sigmas * sigma_ql, ql + num_of_sigmas * sigma_ql
    min_en, max_en = en - num_of_sigmas * sigma_en, en + num_of_sigmas * sigma_en

    pts_q = 20
    sampled_enough = False
    while not sampled_enough:
        # print(pts_q)

        step_qh = (max_qh - min_qh) / pts_q
        step_qk = (max_qk - min_qk) / pts_q
        step_ql = (max_ql - min_ql) / pts_q

        list_qh = np.linspace(min_qh, max_qh, pts_q)
        list_qk = np.linspace(min_qk, max_qk, pts_q)
        list_ql = np.linspace(min_ql, max_ql, pts_q)

        mesh_q = np.meshgrid(list_qh, list_qk, list_ql, indexing="ij")
        vqh, vqk, vql = np.array([np.ravel(v) for v in mesh_q])
        # ----------------------------------------------------
        # determine if sampled enough based on steps along energy
        # ----------------------------------------------------
        disp = model_disp(vqh, vqk, vql)
        num_bands, num_pts = disp.shape
        # ----------------------------------------------------
        # get rid of the ones that are not in the ellipsoid
        # ----------------------------------------------------
        max_disp, min_disp = np.max(disp), np.min(disp)
        if max_disp < min_en or min_disp > max_en:
            return 0.0  # zero intensity

        disp_reshaped = disp.reshape((num_bands, pts_q, pts_q, pts_q))
        idx_inside = np.bitwise_and(disp_reshaped > min_en, disp_reshaped < max_en)
        diff_eh = np.diff(disp_reshaped, axis=1, append=0.0)
        diff_ek = np.diff(disp_reshaped, axis=2, append=0.0)
        diff_el = np.diff(disp_reshaped, axis=3, append=0.0)

        step_eh = np.max(np.mean(np.abs(diff_eh[idx_inside])))
        step_ek = np.max(np.mean(np.abs(diff_ek[idx_inside])))
        step_el = np.max(np.mean(np.abs(diff_el[idx_inside])))
        step_en = np.max((step_eh, step_ek, step_el))

        if step_en > sigma_en / 3:
            print(f"step_en={step_en:.4f} is larger than sigma_em/3={sigma_en / 3:.4f}")
            pts_q *= 2
        else:
            sampled_enough = True

    # ----------------------------------------------------
    # Enough sampled. Calculate weight from resolution function
    # ----------------------------------------------------

    vqe = np.stack(
        (
            np.broadcast_to(vqh, (num_bands, num_pts)) - qh,
            np.broadcast_to(vqk, (num_bands, num_pts)) - qk,
            np.broadcast_to(vql, (num_bands, num_pts)) - ql,
            disp - en,
        ),
        axis=-1,
    )  # shape: (num_bands, num_pts, 4)

    prod = np.einsum("ijk,kl,ijl->ij", vqe, mat, vqe)
    weights = np.exp(-prod / 2)  # shape: (num_bands, num_pts)

    # don't bother if the weight is already too small
    if np.max(weights) < 1e-6:
        return 0.0  # zero intensity

    # ----------------------------------------------------
    # trim the corners
    # ----------------------------------------------------
    cut_off = 1e-6
    idx_all = weights > cut_off
    idx = np.bitwise_or.reduce(idx_all, axis=0)
    # percent = (np.size(idx) - np.count_nonzero(idx)) / np.size(idx) * 100
    # print(f"{percent:.2f}% of points discarded.")

    # all small weights because dispersion parallel to ellipsoid
    if not np.any(idx_all):
        return 0.0  # zero intensity

    # need a correction to enforce the normalization to one
    vq = np.stack((vqh - qh, vqk - qk, vql - ql), axis=-1)
    prod_hkl = np.einsum("ij,jk,ik->i", vq, mat_hkl, vq)
    g_hkl = (np.exp(-prod_hkl / 2)) / np.sqrt(2 * np.pi) ** 3 * np.sqrt(np.linalg.det(mat_hkl))
    correction = np.sum(g_hkl) * step_qh * step_qk * step_ql

    vq_filtered = vq[idx]
    inten = model_inten(vq_filtered[:, 0], vq_filtered[:, 1], vq_filtered[:, 2])
    weights_filtered = weights[:, idx] / correction
    # normalization
    det = np.linalg.det(mat)
    inten_sum = np.sum(inten * weights_filtered) * step_qh * step_qk * step_ql
    return r0 * inten_sum * np.sqrt(det) / (2 * np.pi) ** 2


if __name__ == "__main__":
    # ----------------------------------------------------
    # points being measured
    # qe_mesh has the dimension (4, n_pts_of_measurement)
    # flatten for meshed measurement
    # ----------------------------------------------------
    q1_min, q1_max, q1_step = -1, 1, 0.02
    en_min, en_max, en_step = -3, 25, 0.2
    q2 = 0
    q3 = 0

    q1 = np.linspace(q1_min, q1_max, int((q1_max - q1_min) / q1_step) + 1)
    en = np.linspace(en_min, en_max, int((en_max - en_min) / en_step) + 1)
    vq1, vq2, vq3, ven = np.meshgrid(q1, q2, q3, en, indexing="ij")

    sz = np.shape(vq1)  # sz = (n_q1, n_q2, n_q3 , n_en)
    qe_mesh = np.array([np.ravel(v) for v in (vq1, vq2, vq3, ven)])

    t0 = time()
    num_worker = 8
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_worker) as executor:
        results = executor.map(convolution, *qe_mesh)
    print(f"Convolution completed in {(t1 := time()) - t0:.4f} s")

    measurement_inten = np.array(list(results)).reshape(sz)
    # total intensity should be close to S/2 *(q1_max - q1_min) * 2p*i
    total_intent = np.sum(measurement_inten) * q1_step * en_step / (q1_max - q1_min)

    # ----------------------------------------------------
    # plot 2D contour
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4))
    idx = np.s_[:, 0, 0, :]
    img = ax.pcolormesh(vq1[idx], ven[idx], measurement_inten[idx], cmap="turbo", vmin=0, vmax=0.5)

    ax.grid(alpha=0.6)
    ax.set_xlabel("Q1")
    ax.set_ylabel("En")
    ax.set_xlim((q1_min, q1_max))
    ax.set_ylim((en_min, en_max))

    plot_rez_ellipses(ax)
    disp = model_disp(q1, np.zeros_like(q1), np.zeros_like(q1))
    for i in range(np.shape(disp)[0]):
        ax.plot(q1, disp[i], "-w")

    ax.legend()
    fig.colorbar(img, ax=ax)
    ax.set_title(
        f"1D FM chain S=1 J=-5, total intensity = {total_intent:.3f}"
        + f"\n3D Convolution for {np.shape(qe_mesh)[1]} points completed in {t1 - t0:.3f} s with {num_worker:1d} cores"
    )

    plt.tight_layout()
    plt.show()
