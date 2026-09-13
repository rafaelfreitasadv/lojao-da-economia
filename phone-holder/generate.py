#!/usr/bin/env python3
"""
Suporte de celular para bicicleta ergometrica (console Athletic)
================================================================
Versao BRACADEIRA: abraca o TUBO HORIZONTAL redondo atras do visor
(guidao). Segura o celular DEITADO (paisagem) e EM PE (retrato).

- Canal semicircular por baixo que assenta no tubo (~30-35 mm + espuma).
- Dois tuneis passa-correia: a abracadeira de nylon (zip-tie) OU velcro
  passa por cima (dentro do tunel) e por baixo do tubo, e fecha, puxando
  o suporte firme contra o tubo. Sem furar nada, sem ferramenta.
- Encosto reclinado + calha inferior que segura o celular nas duas posicoes.
- Recorte central para o cabo do carregador e para tirar o celular.

Todas as medidas em MILIMETROS. Ajuste os parametros e rode:
    python3 generate.py
"""

import os
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

# ----------------------------------------------------------------------
# PARAMETROS
# ----------------------------------------------------------------------
# --- Tubo / bracadeira ---
BAR_DIA     = 33.0    # diametro nominal do tubo (usuario: 30-35 mm)
GROOVE_DIA  = 36.0    # canal = tubo + ~1.5 mm de espuma por lado
SADDLE_W    = 72.0    # comprimento da sela ao longo do tubo (X)
SADDLE_D    = 66.0    # profundidade frente-tras (Y)
SADDLE_H    = 40.0    # altura da sela (Z)
TUNNEL_W    = 16.0    # largura de cada tunel passa-correia (X)
TUNNEL_H    = 6.0     # altura de cada tunel (Z)
TUNNEL_XOFF = 18.0    # deslocamento de cada tunel do centro
TUNNEL_Z    = 28.0    # altura do centro do tunel (acima do tubo)

# --- Celular / berco ---
LIP_FRONT_Y   = -20.0  # face frontal do labio (lado do ciclista)
LIP_T         = 7.0    # espessura da parede do labio
LIP_H         = 17.0   # altura do labio acima do topo da sela
PHONE_CHANNEL = 14.0   # folga da calha (traseira do celular encosta no painel)
CABLE_NOTCH_W = 46.0   # recorte central (cabo + dedo)

# --- Encosto ---
BACK_W   = 70.0
BACK_T   = 8.0
BACK_H   = 88.0
RECLINE  = 20.0        # graus a partir da vertical

WALL_OVERLAP = 0.5
CHAMFER      = 3.0

# ----------------------------------------------------------------------
def box(sx, sy, sz):
    return trimesh.creation.box(extents=(sx, sy, sz))

def cyl_x(radius, length, sections=72):
    c = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    c.apply_transform(rotation_matrix(np.pi / 2, [0, 1, 0]))  # eixo -> X
    return c

def tri_prism_yz(pts_yz, thickness_x):
    from shapely.geometry import Polygon
    poly = Polygon(pts_yz)
    m = trimesh.creation.extrude_polygon(poly, height=thickness_x)
    M = np.array([[0, 0, 1, 0],
                  [1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1]], dtype=float)
    m.apply_transform(M)
    return m

def union(meshes):
    return trimesh.boolean.union(meshes, engine='manifold')

def difference(a, b):
    return trimesh.boolean.difference([a, b], engine='manifold')

# ----------------------------------------------------------------------
def build():
    theta = np.radians(RECLINE)
    Z0 = SADDLE_H

    # --- Sela (bloco que assenta no tubo) ---
    saddle = box(SADDLE_W, SADDLE_D, SADDLE_H)
    saddle.apply_translation([0, 0, SADDLE_H / 2.0])

    # --- Labio frontal ---
    lip_bottom = Z0 - 2.0
    lip_top = Z0 + LIP_H
    lip = box(BACK_W, LIP_T, lip_top - lip_bottom)
    lip.apply_translation([0, LIP_FRONT_Y + LIP_T / 2.0,
                           (lip_bottom + lip_top) / 2.0])

    # --- Encosto reclinado (topo tomba para +Y) ---
    panel = box(BACK_W, BACK_T, BACK_H)
    panel.apply_transform(rotation_matrix(-theta, [1, 0, 0]))
    b = panel.bounds
    panel_front_bottom_Y = LIP_FRONT_Y + LIP_T + PHONE_CHANNEL   # = 1.0
    panel.apply_translation([0,
                             panel_front_bottom_Y - b[0][1],
                             (Z0 - WALL_OVERLAP) - b[0][2]])
    pmax_y = panel.bounds[1][1]
    pmax_z = panel.bounds[1][2]

    parts = [saddle, lip, panel]

    # --- Gussets laterais (reforco do encosto sobre a sela) ---
    g_th, g_run, g_h = 8.0, 24.0, 40.0
    ybb = panel_front_bottom_Y + BACK_T * np.cos(theta)
    tri = [(ybb - 2, Z0 - WALL_OVERLAP),
           (ybb - 2, Z0 + g_h),
           (ybb + g_run, Z0 - WALL_OVERLAP)]
    for xoff in (-(BACK_W / 2.0 - g_th), (BACK_W / 2.0 - g_th)):
        g = tri_prism_yz(tri, g_th)
        g.apply_translation([xoff, 0, 0])
        parts.append(g)

    solid = union(parts)

    # --- Canal do tubo (por baixo) ---
    groove = cyl_x(GROOVE_DIA / 2.0, SADDLE_W + 20)
    solid = difference(solid, groove)

    # --- Tuneis passa-correia (frente-tras, por cima do tubo) ---
    for xoff in (-TUNNEL_XOFF, TUNNEL_XOFF):
        t = box(TUNNEL_W, SADDLE_D + 4, TUNNEL_H)
        t.apply_translation([xoff, 0, TUNNEL_Z])
        solid = difference(solid, t)

    # --- Recorte central do cabo ---
    notch = box(CABLE_NOTCH_W, LIP_T + 6, LIP_H + 10)
    notch.apply_translation([0, LIP_FRONT_Y + LIP_T / 2.0,
                             Z0 + (LIP_H + 10) / 2.0 - 4])
    solid = difference(solid, notch)

    # --- Chanfro de conforto no topo do encosto ---
    if CHAMFER > 0:
        cham = box(BACK_W + 4, 30, 30)
        cham.apply_transform(rotation_matrix(np.radians(45), [1, 0, 0]))
        cham.apply_translation([0, pmax_y, pmax_z])
        solid = difference(solid, cham)

    solid.merge_vertices()
    solid.update_faces(solid.nondegenerate_faces())
    solid.fix_normals()
    return solid, pmax_z

# ----------------------------------------------------------------------
def bar_overlay(length=170):
    return cyl_x(BAR_DIA / 2.0, length)

def phone_overlay(orientation):
    theta = np.radians(RECLINE)
    thk = 9.0
    w, h = (150.0, 75.0) if orientation == 'landscape' else (75.0, 150.0)
    ph = box(w, thk, h)
    ph.apply_transform(rotation_matrix(-theta, [1, 0, 0]))
    b = ph.bounds
    ph.apply_translation([0,
                          (LIP_FRONT_Y + LIP_T + 1.0) - b[0][1],
                          (SADDLE_H + 1.0) - b[0][2]])
    return ph

# ----------------------------------------------------------------------
def render(mesh, outfile, elev, azim, extras=None, title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(7, 7), dpi=120)
    ax = fig.add_subplot(111, projection='3d')
    allpts = [mesh.vertices]

    def add(m, facecolor, alpha, shade=True):
        pc = Poly3DCollection(m.triangles, alpha=alpha)
        if shade:
            n = m.face_normals
            light = np.array([0.3, -0.6, 0.75]); light /= np.linalg.norm(light)
            inten = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
            basec = np.array(matplotlib.colors.to_rgb(facecolor))
            pc.set_facecolor(np.clip(basec[None, :] * inten[:, None], 0, 1))
        else:
            pc.set_facecolor(facecolor)
        pc.set_edgecolor((0, 0, 0, 0.0)); pc.set_linewidth(0.0)
        ax.add_collection3d(pc)

    add(mesh, '#f07a2b', 1.0)
    for m, c, a in (extras or []):
        add(m, c, a, shade=(a > 0.6)); allpts.append(m.vertices)

    allpts = np.vstack(allpts)
    mn, mx = allpts.min(0), allpts.max(0)
    ctr = (mn + mx) / 2.0; r = (mx - mn).max() / 2.0 * 1.05
    ax.set_xlim(ctr[0]-r, ctr[0]+r); ax.set_ylim(ctr[1]-r, ctr[1]+r)
    ax.set_zlim(ctr[2]-r, ctr[2]+r)
    try: ax.set_box_aspect((1, 1, 1))
    except Exception: pass
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel('X (largura)'); ax.set_ylabel('Y (frente-tras)')
    ax.set_zlabel('Z (altura)')
    if title: ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3); fig.tight_layout()
    fig.savefig(outfile, bbox_inches='tight'); plt.close(fig)
    print('  render ->', outfile)

# ----------------------------------------------------------------------
def section_drawing(mesh, outfile):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    sec = mesh.section(plane_origin=[30, 0, 0], plane_normal=[1, 0, 0])
    fig, ax = plt.subplots(figsize=(8, 7.5), dpi=120)
    for poly in sec.discrete:
        ax.fill(poly[:, 1], poly[:, 2], facecolor='#f5b183',
                edgecolor='#c0561a', linewidth=1.6, zorder=2)

    # tubo
    ang = np.linspace(0, 2*np.pi, 80)
    ax.plot((BAR_DIA/2)*np.cos(ang), (BAR_DIA/2)*np.sin(ang),
            '--', color='#555', lw=1.5, zorder=3)
    ax.text(0, -BAR_DIA/2 - 6, f'tubo ~{BAR_DIA:.0f} mm', color='#555',
            ha='center', fontsize=10)

    # celular
    th = np.radians(RECLINE)
    p0 = np.array([LIP_FRONT_Y + LIP_T, SADDLE_H])
    p1 = p0 + np.array([np.sin(th), np.cos(th)]) * 150
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#222', lw=6,
            solid_capstyle='round', alpha=0.55, zorder=1)
    ax.text(p1[0]+3, p1[1], 'celular', color='#222', fontsize=10, va='center')

    def dim(x0, y0, x1, y1, txt, off=(0, 0)):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='<->', color='#1560a8', lw=1.3))
        ax.text((x0+x1)/2+off[0], (y0+y1)/2+off[1], txt, color='#1560a8',
                fontsize=10, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))

    tot_h = mesh.bounds[1][2] - mesh.bounds[0][2]
    dim(-SADDLE_D/2, -BAR_DIA/2-14, SADDLE_D/2, -BAR_DIA/2-14,
        f'sela {SADDLE_D:.0f} mm', off=(0, -3))
    dim(LIP_FRONT_Y, SADDLE_H+LIP_H+4, LIP_FRONT_Y+LIP_T+PHONE_CHANNEL,
        SADDLE_H+LIP_H+4, f'calha {PHONE_CHANNEL:.0f} mm', off=(0, 4))
    ax.text(TUNNEL_XOFF+2, TUNNEL_Z, 'tunel\ncorreia', color='#1560a8',
            fontsize=8, va='center')
    ax.text(30, SADDLE_H+50, f'~{RECLINE:.0f}deg', color='#c0561a', fontsize=11)

    ax.set_aspect('equal')
    ax.set_xlabel('frente  <-  Y (mm)  ->  tras')
    ax.set_ylabel('altura Z (mm)  (0 = centro do tubo)')
    ax.set_title('Corte lateral cotado - bracadeira no tubo', fontsize=12)
    ax.grid(True, alpha=0.25); ax.margins(0.15)
    fig.tight_layout(); fig.savefig(outfile, bbox_inches='tight'); plt.close(fig)
    print('  render ->', outfile)

# ----------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    mesh, pmax_z = build()

    stl = os.path.join(here, 'bike_phone_holder.stl')
    mesh.export(stl)
    vol_cm3 = mesh.volume / 1000.0
    print('STL exportado ->', stl)
    print('  watertight:', mesh.is_watertight, '| triangulos:', len(mesh.faces))
    print('  dimensoes (mm) L x P x A: %.1f x %.1f x %.1f'
          % tuple((mesh.bounds[1] - mesh.bounds[0])))
    print('  volume solido: %.1f cm3' % vol_cm3)
    print('  filamento estimado (~3 paredes+20%% infill): %.0f g'
          % (vol_cm3 * 0.36 * 1.24))

    bar = (bar_overlay(), '#888888', 0.4)
    render(mesh, os.path.join(here, 'preview_1_perspectiva.png'),
           elev=20, azim=-60, extras=[bar],
           title='Bracadeira no tubo (tubo em cinza)')
    render(mesh, os.path.join(here, 'preview_2_lateral.png'),
           elev=6, azim=-90, extras=[bar, (phone_overlay('portrait'), '#1a1a1a', 0.35)],
           title='Lateral - celular EM PE (retrato)')
    render(mesh, os.path.join(here, 'preview_3_deitado.png'),
           elev=16, azim=-54, extras=[bar, (phone_overlay('landscape'), '#1a1a1a', 0.35)],
           title='Celular DEITADO (paisagem) - assistir video')
    render(mesh, os.path.join(here, 'preview_4_base.png'),
           elev=-60, azim=-90, extras=[bar],
           title='Vista de baixo - canal do tubo + tuneis da correia')
    section_drawing(mesh, os.path.join(here, 'preview_5_cotas.png'))
    print('OK')


if __name__ == '__main__':
    main()
