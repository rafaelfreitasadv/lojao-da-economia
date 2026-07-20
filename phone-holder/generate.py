#!/usr/bin/env python3
"""
Suporte de celular para bicicleta ergometrica (console Athletic)
================================================================
Gera um berco universal que APOIA sobre o topo do painel e segura o
celular tanto DEITADO (paisagem) quanto EM PE (retrato).

- Base de apoio com duas alcas (passadores) para prender com fita
  velcro / abracadeira ao console (trava contra a vibracao do pedal).
- Encosto reclinado + calha inferior que segura o celular.
- Recorte central para o cabo do carregador e para tirar o celular.

Todas as medidas em MILIMETROS. Ajuste os parametros abaixo e rode:
    python3 generate.py
Saidas: bike_phone_holder.stl + imagens de previa (PNG).
"""

import os
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

# ----------------------------------------------------------------------
# PARAMETROS  (edite aqui e rode de novo para gerar sob medida)
# ----------------------------------------------------------------------
# --- Celular / berco ---
PHONE_CHANNEL = 14.0    # folga da calha p/ a base do celular (traseira encosta no painel)
LIP_FRONT     = 26.0    # posicao da face frontal do labio (=tamanho do pe da frente)
LIP_T         = 7.0     # espessura da parede do labio (frente da calha)
LIP_H         = 17.0    # altura do labio acima da base (segura o celular)
CABLE_NOTCH_W = 46.0    # largura do recorte central (cabo + dedo)

# --- Encosto ---
BACK_W   = 112.0        # largura do encosto
BACK_T   = 8.0          # espessura do encosto
BACK_H   = 92.0         # altura do encosto
RECLINE  = 22.0         # inclinacao do encosto (graus a partir da vertical)

# --- Base ---
BASE_W       = 116.0    # largura da base
BASE_T       = 7.0      # espessura da base
BASE_REARPAD = 8.0      # sobra da base atras do encosto

# --- Alcas p/ correia (passadores) ---
STRAP_SLOTS   = True
SLOT_W        = 30.0    # largura de cada passador (X)
SLOT_Y0       = 10.0    # inicio do passador (Y)
SLOT_Y1       = 18.0    # fim do passador (Y)
SLOT_XOFF     = 34.0    # deslocamento do centro de cada passador

WALL_OVERLAP = 0.5      # sobreposicao p/ uniao solida
CHAMFER      = 3.0      # chanfro de conforto no topo do encosto

# ----------------------------------------------------------------------
def box(sx, sy, sz):
    return trimesh.creation.box(extents=(sx, sy, sz))

def tri_prism_yz(pts_yz, thickness_x):
    """Prisma triangular: triangulo no plano Y-Z, espessura ao longo de X.
    Retorna malha com X em [0, thickness_x]."""
    from shapely.geometry import Polygon
    poly = Polygon(pts_yz)                     # coords interpretadas como (px, py)
    m = trimesh.creation.extrude_polygon(poly, height=thickness_x)
    # extrude: px->world X? Na verdade extrude poe poligono no plano XY (px=X, py=Y)
    # e extruda em Z. Queremos: px(=Y) -> world Y, py(=Z) -> world Z, esp -> world X.
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

    # --- Encosto reclinado: topo tomba para +Y (para tras) ---
    panel = box(BACK_W, BACK_T, BACK_H)
    panel.apply_transform(rotation_matrix(-theta, [1, 0, 0]))  # +Z tomba p/ +Y
    b = panel.bounds
    panel_front_bottom_Y = LIP_FRONT + LIP_T + PHONE_CHANNEL    # = 51 c/ default
    dz = (BASE_T - WALL_OVERLAP) - b[0][2]
    dy = panel_front_bottom_Y - b[0][1]
    panel.apply_translation([0, dy, dz])
    pmax_y = panel.bounds[1][1]
    pmax_z = panel.bounds[1][2]

    base_d = pmax_y + BASE_REARPAD

    # --- Base ---
    base = box(BASE_W, base_d, BASE_T)
    base.apply_translation([0, base_d / 2.0, BASE_T / 2.0])

    # --- Labio frontal (frente da calha) com recorte de cabo ---
    lip_z = BASE_T + LIP_H
    lip = box(BACK_W, LIP_T, lip_z)
    lip.apply_translation([0, LIP_FRONT + LIP_T / 2.0, lip_z / 2.0])

    parts = [base, panel, lip]

    # --- Gussets laterais (reforco atras do encosto) ---
    g_th = 8.0
    g_run = 26.0
    g_h = 42.0
    ybb = panel_front_bottom_Y + BACK_T * np.cos(theta)  # ~face de tras na base
    tri = [(ybb - 2, BASE_T - WALL_OVERLAP),
           (ybb - 2, BASE_T + g_h),
           (ybb + g_run, BASE_T - WALL_OVERLAP)]
    for xoff in (-(BACK_W / 2.0 - g_th), (BACK_W / 2.0 - g_th)):
        g = tri_prism_yz(tri, g_th)
        g.apply_translation([xoff, 0, 0])
        parts.append(g)

    solid = union(parts)

    # --- Recorte central: cabo + pega-dedo (atravessa o labio) ---
    notch = box(CABLE_NOTCH_W, LIP_T + 4, LIP_H + 6)
    notch.apply_translation([0, LIP_FRONT + LIP_T / 2.0, BASE_T + (LIP_H + 6) / 2.0])
    solid = difference(solid, notch)

    # --- Chanfro de conforto no topo do encosto ---
    if CHAMFER > 0:
        cham = box(BACK_W + 4, 30, 30)
        cham.apply_transform(rotation_matrix(np.radians(45), [1, 0, 0]))
        cham.apply_translation([0, panel.bounds[1][1], pmax_z])
        solid = difference(solid, cham)

    # --- Passadores para correia ---
    if STRAP_SLOTS:
        for xoff in (-SLOT_XOFF, SLOT_XOFF):
            slot = box(SLOT_W, SLOT_Y1 - SLOT_Y0, BASE_T + 2)
            slot.apply_translation([xoff, (SLOT_Y0 + SLOT_Y1) / 2.0, BASE_T / 2.0])
            solid = difference(solid, slot)

    solid.merge_vertices()
    solid.update_faces(solid.nondegenerate_faces())
    solid.fix_normals()
    return solid, base_d, pmax_z

# ----------------------------------------------------------------------
def phone_overlay(orientation, base_d):
    """Caixa translucida representando o celular no berco (ilustracao)."""
    theta = np.radians(RECLINE)
    thk = 9.0
    if orientation == 'landscape':
        w, h = 150.0, 75.0
    else:
        w, h = 75.0, 150.0
    ph = box(w, thk, h)
    ph.apply_transform(rotation_matrix(-theta, [1, 0, 0]))
    b = ph.bounds
    # apoia a base do celular na calha, encostado no painel
    ph.apply_translation([0,
                          (LIP_FRONT + LIP_T + 1.0) - b[0][1],
                          (BASE_T + 1.0) - b[0][2]])
    return ph

# ----------------------------------------------------------------------
def render(mesh, outfile, elev, azim, phone=None, title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(7, 7), dpi=120)
    ax = fig.add_subplot(111, projection='3d')

    def add(m, facecolor, alpha, shade=True):
        tris = m.triangles
        pc = Poly3DCollection(tris, alpha=alpha)
        if shade:
            n = m.face_normals
            light = np.array([0.3, -0.6, 0.75]); light = light / np.linalg.norm(light)
            inten = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
            base = np.array(matplotlib.colors.to_rgb(facecolor))
            cols = np.clip(base[None, :] * inten[:, None], 0, 1)
            pc.set_facecolor(cols)
        else:
            pc.set_facecolor(facecolor)
        pc.set_edgecolor((0, 0, 0, 0.0))
        pc.set_linewidth(0.0)
        ax.add_collection3d(pc)

    add(mesh, '#f07a2b', 1.0)          # laranja (cor Athletic)
    if phone is not None:
        add(phone, '#1a1a1a', 0.35, shade=False)

    allpts = mesh.vertices if phone is None else np.vstack([mesh.vertices, phone.vertices])
    mn, mx = allpts.min(0), allpts.max(0)
    ctr = (mn + mx) / 2.0
    r = (mx - mn).max() / 2.0 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel('X  (largura)')
    ax.set_ylabel('Y  (frente-tras)')
    ax.set_zlabel('Z  (altura)')
    if title:
        ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outfile, bbox_inches='tight')
    plt.close(fig)
    print('  render ->', outfile)

# ----------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    mesh, base_d, pmax_z = build()

    stl = os.path.join(here, 'bike_phone_holder.stl')
    mesh.export(stl)
    vol_cm3 = mesh.volume / 1000.0
    print('STL exportado ->', stl)
    print('  watertight:', mesh.is_watertight,
          '| triangulos:', len(mesh.faces))
    print('  dimensoes (mm)  L x P x A: %.1f x %.1f x %.1f'
          % tuple((mesh.bounds[1] - mesh.bounds[0])))
    print('  volume solido: %.1f cm3' % vol_cm3)
    # estimativa material: parede+15%% infill ~ 32%% do solido, PLA 1.24 g/cm3
    print('  filamento estimado (~2 paredes+15%% infill): %.0f g'
          % (vol_cm3 * 0.32 * 1.24))

    render(mesh, os.path.join(here, 'preview_1_perspectiva.png'),
           elev=22, azim=-58, title='Suporte - perspectiva')
    render(mesh, os.path.join(here, 'preview_2_lateral.png'),
           elev=6, azim=-90, phone=phone_overlay('portrait', base_d),
           title='Lateral - celular EM PE (retrato)')
    render(mesh, os.path.join(here, 'preview_3_deitado.png'),
           elev=16, azim=-52, phone=phone_overlay('landscape', base_d),
           title='Celular DEITADO (paisagem) - assistir video')
    render(mesh, os.path.join(here, 'preview_4_base.png'),
           elev=-62, azim=-90, title='Vista de baixo - passadores da correia')
    section_drawing(mesh, os.path.join(here, 'preview_5_cotas.png'))
    print('OK')


def section_drawing(mesh, outfile):
    """Corte lateral EXATO (tirado da malha) com cotas, plano X=40mm."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    sec = mesh.section(plane_origin=[40, 0, 0], plane_normal=[1, 0, 0])
    fig, ax = plt.subplots(figsize=(8, 7), dpi=120)
    for poly in sec.discrete:            # cada poly: pontos 3D no plano
        ax.fill(poly[:, 1], poly[:, 2], facecolor='#f5b183',
                edgecolor='#c0561a', linewidth=1.6, zorder=2)

    # celular (retrato) encostado, so ilustracao
    th = np.radians(RECLINE)
    y0, z0 = LIP_FRONT + LIP_T, BASE_T          # base do celular na calha
    L = 150.0
    dirp = np.array([np.sin(th), np.cos(th)])   # sobe e recua
    p0 = np.array([y0, z0]); p1 = p0 + dirp * L
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#222', lw=6,
            solid_capstyle='round', alpha=0.55, zorder=1)
    ax.text(p1[0] + 3, p1[1], 'celular', color='#222', fontsize=10, va='center')

    tot_h = (mesh.bounds[1][2] - mesh.bounds[0][2])
    base_d = mesh.bounds[1][1] - mesh.bounds[0][1]

    def dim(x0, y0_, x1, y1_, txt, off=(0, 0)):
        ax.annotate('', xy=(x1, y1_), xytext=(x0, y0_),
                    arrowprops=dict(arrowstyle='<->', color='#1560a8', lw=1.3))
        ax.text((x0 + x1) / 2 + off[0], (y0_ + y1_) / 2 + off[1], txt,
                color='#1560a8', fontsize=10, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))

    dim(0, -9, base_d, -9, f'profundidade base {base_d:.0f} mm', off=(0, -3))
    dim(-8, 0, -8, tot_h, f'altura {tot_h:.0f} mm', off=(-4, 0))
    dim(LIP_FRONT, BASE_T + LIP_H + 4, LIP_FRONT + LIP_T + PHONE_CHANNEL,
        BASE_T + LIP_H + 4, f'calha {PHONE_CHANNEL:.0f} mm', off=(0, 4))
    dim(LIP_FRONT + LIP_T + PHONE_CHANNEL + 5, BASE_T,
        LIP_FRONT + LIP_T + PHONE_CHANNEL + 5, BASE_T + LIP_H,
        f'labio {LIP_H:.0f} mm', off=(16, 0))
    # arco do angulo de reclinacao
    ax.text(y0 + 20, z0 + 26, f'~{RECLINE:.0f}deg', color='#c0561a', fontsize=11)

    ax.set_aspect('equal')
    ax.set_xlabel('frente  <-  Y (mm)  ->  tras')
    ax.set_ylabel('altura Z (mm)')
    ax.set_title('Corte lateral cotado (celular EM PE ilustrado)', fontsize=12)
    ax.grid(True, alpha=0.25)
    ax.margins(0.18)
    fig.tight_layout()
    fig.savefig(outfile, bbox_inches='tight')
    plt.close(fig)
    print('  render ->', outfile)


if __name__ == '__main__':
    main()
