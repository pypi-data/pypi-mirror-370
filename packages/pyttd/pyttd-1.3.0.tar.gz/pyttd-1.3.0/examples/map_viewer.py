#!/usr/bin/env python3
"""
Interactive map viewer using pygame with colored tiles based on tile type and height shading.

Usage:
  python examples/map_viewer.py /path/to/savegame.sav
"""

import sys
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import argparse
import time
import logging
import logging
import pygame
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyttd.saveload import load_savefile
from pyttd import OpenTTDClient
from pyttd.saveload.map_flatbuffers import MapFB
from pyttd.saveload.tiles import (
    decode_tile_type,
    decode_owner,
    decode_industry_info,
    industry_type_display,
)


PALETTE = {
    0: (60, 180, 75),  # MP_CLEAR
    1: (130, 130, 130),  # MP_RAILWAY
    2: (90, 90, 90),  # MP_ROAD
    3: (210, 190, 170),  # MP_HOUSE
    4: (34, 139, 34),  # MP_TREES
    5: (200, 130, 0),  # MP_STATION
    6: (30, 144, 255),  # MP_WATER
    7: (0, 0, 0),  # MP_VOID
    8: (190, 190, 0),  # MP_INDUSTRY
    9: (150, 100, 150),  # MP_TUNNELBRIDGE
    10: (220, 220, 220),  # MP_OBJECT
}

TILE_TYPE_NAME: Dict[int, str] = {
    0: "Clear",
    1: "Railway",
    2: "Road/Tram",
    3: "House",
    4: "Trees",
    5: "Station",
    6: "Water",
    7: "Void",
    8: "Industry",
    9: "Tunnel/Bridge",
    10: "Object",
}


def shade_color(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    r, g, b = rgb
    return (
        int(max(0, min(255, r * factor))),
        int(max(0, min(255, g * factor))),
        int(max(0, min(255, b * factor))),
    )


def build_color_image(width: int, height: int, types_full: List[int], heights: List[int]):
    # Decode type: upper nibble (bits 4..7)
    types = [((t >> 4) & 0x0F) for t in types_full]
    max_h = max(1, max(heights) if heights else 1)
    if np is None:
        # Return a list of row-wise color tuples
        rows = []
        for y in range(height):
            row = []
            for x in range(width):
                t = types[y * width + x]
                h = heights[y * width + x]
                base = PALETTE.get(t, (255, 0, 255))
                factor = 0.65 + 0.35 * (h / max_h)
                row.append(shade_color(base, factor))
            rows.append(row)
        return rows
    else:
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        types_arr = np.array(types, dtype=np.uint16).reshape(height, width)
        heights_arr = np.array(heights, dtype=np.float32).reshape(height, width)
        factor = 0.65 + 0.35 * (heights_arr / max_h)

        # Assign base colors via palette
        for t, color in PALETTE.items():
            mask = types_arr == t
            if not np.any(mask):
                continue
            r, g, b = color
            arr[mask] = (r, g, b)
        # Unknown types -> magenta
        unknown_mask = ~np.isin(types_arr, np.array(list(PALETTE.keys())))
        arr[unknown_mask] = (255, 0, 255)

        # Apply shading
        arr = (arr.astype(np.float32) * factor[..., None]).clip(0, 255).astype(np.uint8)
        return arr


def main():
    # Two modes:
    # 1) Offline: python examples/map_viewer.py <savefile_path>
    # 2) Live:    python examples/map_viewer.py --live --host 127.0.0.1 --port 3979 --name Viewer
    parser = argparse.ArgumentParser(description="OpenTTD Map Viewer (offline or live)")
    parser.add_argument("savefile", nargs="?", help="Path to savefile for offline mode")
    parser.add_argument("--live", action="store_true", help="Connect to a live server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=3979, help="Server port")
    parser.add_argument("--name", default="Viewer", help="Player name when live")
    args = parser.parse_args()

    pygame.init()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    progress_screen = pygame.display.set_mode((640, 120))
    pygame.display.set_caption("Loading map...")
    font = pygame.font.SysFont(None, 22)

    progress_value = 0.0
    progress_stage = "starting"

    def draw_progress():
        progress_screen.fill((25, 25, 25))

        title = font.render("Parsing map...", True, (220, 220, 220))
        progress_screen.blit(title, (10, 10))

        bar_x, bar_y, bar_w, bar_h = 10, 50, 620, 20
        pygame.draw.rect(progress_screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), 1)
        fill_w = int(bar_w * max(0.0, min(1.0, progress_value)))
        pygame.draw.rect(
            progress_screen,
            (100, 180, 100),
            (bar_x + 1, bar_y + 1, fill_w - 2 if fill_w > 2 else 0, bar_h - 2),
        )

        stage = font.render(f"{progress_value*100:.0f}% - {progress_stage}", True, (200, 200, 200))
        progress_screen.blit(stage, (10, 80))
        pygame.display.flip()

    def progress_cb(p: float, stage: str):
        nonlocal progress_value, progress_stage
        progress_value, progress_stage = p, stage

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        draw_progress()

    # Initial draw
    draw_progress()

    if args.live:
        client = OpenTTDClient(server=args.host, port=args.port, player_name=args.name)
        map_ready = {"ok": False}

        def on_map_parsed():
            map_ready["ok"] = True

        def on_map_complete():
            nonlocal progress_stage
            progress_stage = "map received; parsing in background..."

        def on_progress(p: float, stage: str):
            nonlocal progress_value, progress_stage

            progress_value = p
            progress_stage = stage

        # Wait for parsed map to be ready
        client.on("map_parsed", on_map_parsed)
        client.on("map_complete", on_map_complete)
        client.on("map_parse_progress", on_progress)
        client.connect()
        # Spin until map arrives
        while not map_ready["ok"]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            draw_progress()
            pygame.time.delay(50)

        # Use parsed save from client
        parsed = client.get_parsed_save()
        if parsed is None:
            print("Failed to get savefile from server")
            return
        title_name = f"{args.host}:{args.port}"
    else:
        if not args.savefile:
            print("Usage: python examples/map_viewer.py <savefile_path> or --live ...")
            return
        savefile = args.savefile
        title = font.render(f"Parsing: {Path(savefile).name}", True, (220, 220, 220))
        progress_screen.blit(title, (10, 10))
        pygame.display.flip()
        parsed = load_savefile(savefile, parsed=True, silent=True, progress_callback=progress_cb)
        title_name = Path(savefile).name
    fb = parsed.map.flatbuffers_map
    if not fb:
        print("No FlatBuffers map present.")
        return

    m = MapFB.GetRootAsMapFB(fb, 0)
    width = m.Width()
    height = m.Height()
    size = width * height
    types = [m.Type(i) for i in range(size)]
    heights = [m.Heightmap(i) for i in range(size)]
    m1 = [m.M1(i) for i in range(size)]
    m2 = [m.M2(i) for i in range(size)]
    m3 = [m.M3(i) for i in range(size)]
    m4 = [m.M4(i) for i in range(size)]
    m5 = [m.M5(i) for i in range(size)]
    m6 = [m.M6(i) for i in range(size)]
    m7 = [m.M7(i) for i in range(size)]
    m8 = [m.M8(i) for i in range(size)]

    pygame.display.set_caption(f"pyttd map viewer - {title_name} ({width}x{height})")

    # Company info lookup for owners
    company_names: Dict[int, str] = {}
    company_info_by_id: Dict[int, Dict[str, str]] = {}
    try:
        for c in getattr(parsed.companies, "companies", []):
            cid = int(c.get("id", -1))
            name = str(c.get("name", f"Company {cid}"))
            if 0 <= cid <= 14:
                company_names[cid] = name
                color = c.get("color", {})
                company_info_by_id[cid] = {
                    "name": name,
                    "color_name": str(color.get("name", "")),
                    "color_index": str(color.get("index", "")),
                }
    except Exception:
        pass

    # Industry lookup by index -> raw dict
    industry_by_index: Dict[int, Dict[str, Any]] = {}
    try:
        for ind in parsed.raw_data.get("indy", []):
            idx = int(ind.get("index", -1))
            if idx >= 0:
                industry_by_index[idx] = ind
    except Exception:
        pass

    # Initial view settings with rotation support
    rotation_quads = 0  # 0,1,2,3 (90-deg steps clockwise)
    offset_x = 0
    offset_y = 0

    # If live, subscribe to server actions and flash highlights
    active_highlights: List[Tuple[int, int, int]] = []  # (x, y, ttl_frames)
    # Persistent overlay of constructed tiles (tile_type index)
    overlay_tiles: Dict[Tuple[int, int], int] = {}

    if "client" in locals():
        import queue

        action_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

        def on_server_action(action: Dict[str, Any]):
            # Enqueue for main-thread processing
            action_queue.put(action)

        client.on("server_action", on_server_action)

        # Also log raw server_command in case tile decode fails
        def on_server_command(company, cmd, frame, cb):
            logging.info(f"SERVER_COMMAND: company={company}, cmd={cmd}, frame={frame}, cb={cb}")

        client.on("server_command", on_server_command)

    di = pygame.display.Info()
    screen_w = max(640, min(1600, di.current_w - 40))
    screen_h = max(480, min(1000, di.current_h - 80))
    win_w = min(1400, screen_w)
    win_h = min(900, screen_h)

    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)

    def rotated_dims() -> Tuple[int, int]:
        if rotation_quads % 2 == 0:
            return width, height
        return height, width

    def fit_zoom_for_window() -> int:
        rw, rh = rotated_dims()
        return max(1, min((win_w - 8) // rw, (win_h - 8) // rh))

    zoom = min(8, fit_zoom_for_window())

    base = build_color_image(width, height, types, heights)

    # Option to flip vertically/horizontally to match game orientation
    flip_vertical = False
    flip_horizontal = True

    def render_surface(scale: int) -> pygame.Surface:
        # Build unrotated surface
        if np is not None and isinstance(base, np.ndarray):
            img = base
            if flip_vertical:
                img = np.flipud(img)
            if flip_horizontal:
                img = np.fliplr(img)
            surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
            if scale != 1:
                surf = pygame.transform.scale(surf, (width * scale, height * scale))
        else:
            surf = pygame.Surface((width * scale, height * scale))
            row_iter = range(height - 1, -1, -1) if flip_vertical else range(height)
            for yi, y in enumerate(row_iter):
                xs = range(width - 1, -1, -1) if flip_horizontal else range(width)
                for xi, x in enumerate(xs):
                    color = base[y][x]
                    py = yi if flip_vertical else y
                    px = xi if flip_horizontal else x
                    pygame.draw.rect(surf, color, (px * scale, py * scale, scale, scale))
        # Apply rotation in 90-degree steps (clockwise)
        if rotation_quads % 4 != 0:
            angle = -90 * (rotation_quads % 4)
            surf = pygame.transform.rotate(surf, angle)
        return surf

    map_surf = render_surface(zoom)

    def clamp_offsets():
        nonlocal offset_x, offset_y
        max_x = max(0, map_surf.get_width() - win_w)
        max_y = max(0, map_surf.get_height() - win_h)
        if offset_x < 0:
            offset_x = 0
        if offset_y < 0:
            offset_y = 0
        if offset_x > max_x:
            offset_x = max_x
        if offset_y > max_y:
            offset_y = max_y

    def refit_and_center():
        nonlocal zoom, offset_x, offset_y, map_surf
        zoom = min(16, max(1, fit_zoom_for_window()))
        map_surf = render_surface(zoom)
        offset_x = max(0, (map_surf.get_width() - win_w) // 2)
        offset_y = max(0, (map_surf.get_height() - win_h) // 2)
        clamp_offsets()

    # Mouse state
    dragging = False
    drag_last: Tuple[int, int] = (0, 0)
    hovered: Optional[Tuple[int, int]] = None
    selected: Optional[Tuple[int, int]] = None

    def tile_to_rotated_px(tx: int, ty: int) -> Tuple[int, int]:
        # Convert to display coords: top-right origin (horizontal flip only)
        ty2 = ty
        tx2 = (width - 1) - tx if flip_horizontal else tx
        # Apply rotation (clockwise)
        if rotation_quads % 4 == 1:
            rx = (height - 1) - ty2
            ry = tx2
        elif rotation_quads % 4 == 2:
            rx = (width - 1) - tx2
            ry = (height - 1) - ty2
        elif rotation_quads % 4 == 3:
            rx = ty2
            ry = (width - 1) - tx2
        else:
            rx = tx2
            ry = ty2
        return rx * zoom, ry * zoom

    def screen_to_tile(mx: int, my: int) -> Optional[Tuple[int, int]]:
        # Convert screen coords to rotated surface coords
        rx = offset_x + mx
        ry = offset_y + my
        if rx < 0 or ry < 0 or rx >= map_surf.get_width() or ry >= map_surf.get_height():
            return None
        # Tile coords in rotated space
        xr = rx // zoom
        yr = ry // zoom
        # Invert rotation
        if rotation_quads % 4 == 1:
            tx2 = yr
            ty2 = (height - 1) - xr
        elif rotation_quads % 4 == 2:
            tx2 = (width - 1) - xr
            ty2 = (height - 1) - yr
        elif rotation_quads % 4 == 3:
            tx2 = (width - 1) - yr
            ty2 = xr
        else:
            tx2 = xr
            ty2 = yr
        # Invert horizontal mapping back to array coords
        ty = ty2
        tx = (width - 1) - tx2 if flip_horizontal else tx2
        if 0 <= tx < width and 0 <= ty < height:
            return tx, ty
        return None

    def get_tile_info(tx: int, ty: int) -> Dict[str, str]:
        idx = ty * width + tx
        tbyte = types[idx]
        tile_type = decode_tile_type(tbyte)
        tropic = tbyte & 0x03
        bridge = (tbyte >> 2) & 0x03
        info: Dict[str, str] = {}
        info["Tile"] = f"({tx}, {ty}) index={idx}"
        info["Type"] = f"{tile_type} ({TILE_TYPE_NAME.get(tile_type, 'Unknown')})"
        info["Height"] = str(heights[idx])
        info["m1"] = str(m1[idx])
        info["m2"] = str(m2[idx])
        info["m3"] = str(m3[idx])
        info["m4"] = str(m4[idx])
        info["m5"] = str(m5[idx])
        info["m6"] = str(m6[idx])
        info["m7"] = str(m7[idx])
        info["m8"] = str(m8[idx])
        # Owner (non-industry/house)
        owner_id = decode_owner(tbyte, m1[idx])
        if owner_id is not None:
            # Company names are prepared above
            from_name = company_names.get(owner_id)
            if from_name is None:
                if owner_id == 0x0F:
                    owner_disp = f"{owner_id} (Town)"
                elif owner_id == 0x10:
                    owner_disp = f"{owner_id} (None)"
                elif owner_id == 0x11:
                    owner_disp = f"{owner_id} (Water)"
                elif owner_id == 0x12:
                    owner_disp = f"{owner_id} (Deity)"
                else:
                    owner_disp = f"{owner_id} (Company {owner_id})"
            else:
                owner_disp = f"{owner_id} ({from_name})"
            info["Owner"] = owner_disp
        else:
            info["Owner"] = "N/A"

        # Industry
        if tile_type == 8:
            ind = decode_industry_info(
                m1[idx], m2[idx], m3[idx], m4[idx], m5[idx], m6[idx], m7[idx]
            )
            info["IndustryID"] = str(ind["industry_id"])
            raw_ind = industry_by_index.get(ind["industry_id"], {})
            itype = int(raw_ind.get("type", -1))
            info["IndustryType"] = industry_type_display(itype)
            # Industry owner, if present in INDY
            ind_owner = raw_ind.get("owner")
            if ind_owner is not None:
                ind_owner = int(ind_owner)
                ci = company_info_by_id.get(ind_owner)
                if ci is not None:
                    info["IndustryOwner"] = f"{ind_owner} ({ci['name']})"
                else:
                    info["IndustryOwner"] = str(ind_owner)
            # Location (tile index to x,y)
            loc = raw_ind.get("location")
            if isinstance(loc, int):
                ix = loc % width
                iy = loc // width
                info["IndustryLocation"] = f"({ix}, {iy}) tile={loc}"
            info["Construction"] = (
                "completed"
                if ind["completed"]
                else f"stage={ind['construction_stage']} counter={ind['construction_counter']}"
            )
            info["Anim"] = f"loop={ind['anim_loop']} frame={ind['anim_frame']}"
            info["GfxID"] = str(ind["gfx_id"])

        info["Flags"] = f"tropic={tropic} bridgebits={bridge}"
        return info

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update window size and refit
                win_w, win_h = max(320, event.w), max(240, event.h)
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                refit_and_center()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 2, 3):
                    dragging = True
                    drag_last = event.pos
                if event.button == 1:
                    tile = screen_to_tile(*event.pos)
                    if tile is not None:
                        selected = tile
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 2, 3):
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx, my = event.pos
                    lx, ly = drag_last
                    dx = mx - lx
                    dy = my - ly
                    offset_x = max(0, min(max(0, map_surf.get_width() - win_w), offset_x - dx))
                    offset_y = max(0, min(max(0, map_surf.get_height() - win_h), offset_y - dy))
                    drag_last = event.pos
                # Update hover
                hovered = screen_to_tile(*event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                before_x = offset_x + mx
                before_y = offset_y + my
                if event.y > 0:
                    new_zoom = min(16, zoom + 1)
                elif event.y < 0:
                    new_zoom = max(1, zoom - 1)
                else:
                    new_zoom = zoom
                if new_zoom != zoom:
                    old_zoom = zoom
                    zoom = new_zoom
                    map_surf = render_surface(zoom)
                    factor = zoom / old_zoom
                    offset_x = int(before_x * factor - mx)
                    offset_y = int(before_y * factor - my)
                    clamp_offsets()

        # Process queued server actions (main thread)
        if "action_queue" in locals():
            while True:
                try:
                    action = action_queue.get_nowait()
                except Exception:
                    break
                tiles_xy = action.get("tiles_xy")
                points: List[Tuple[int, int]] = []
                if isinstance(tiles_xy, list) and tiles_xy:
                    points.extend([(int(px), int(py)) for px, py in tiles_xy])
                txy = action.get("tile_xy")
                if isinstance(txy, tuple) and len(txy) == 2:
                    points.append((int(txy[0]), int(txy[1])))

                # Flash highlights for all points
                for x, y in points:
                    active_highlights.append((x, y, 90))

                # Apply updates to underlying arrays
                if action.get("is_construction") and points:
                    category = action.get("construction_category")
                    category_to_type = {
                        "road": 2,
                        "rail": 1,
                        "station": 5,
                        "industry": 8,
                        "tunnel_bridge": 9,
                        "object": 10,
                        "landscaping": 0,
                    }
                    over_type = category_to_type.get(str(category))
                    company = action.get("company")
                    for x, y in points:
                        idx = y * width + x
                        if 0 <= idx < len(types) and over_type is not None:
                            types[idx] = (over_type << 4) | (types[idx] & 0x0F)
                            if (
                                isinstance(company, int)
                                and 0 <= company <= 31
                                and 0 <= idx < len(m1)
                            ):
                                m1[idx] = (m1[idx] & ~0x1F) | company
                    # Rebuild once after mutations
                    base = build_color_image(width, height, types, heights)
                    map_surf = render_surface(zoom)
                    logging.info(f"Applied live update to {len(points)} tile(s) for {category}")

        screen.fill((0, 0, 0))
        screen.blit(map_surf, (-offset_x, -offset_y))

        # Draw persistent overlays for constructed tiles
        if overlay_tiles:
            max_h = max(1, max(heights) if heights else 1)
            for (ox, oy), otype in overlay_tiles.items():
                if 0 <= ox < width and 0 <= oy < height:
                    px, py = tile_to_rotated_px(ox, oy)
                    idx = oy * width + ox
                    h = heights[idx]
                    base = PALETTE.get(otype, (255, 0, 255))
                    factor = 0.65 + 0.35 * (h / max_h)
                    col = shade_color(base, factor)
                    pygame.draw.rect(screen, col, (px - offset_x, py - offset_y, zoom, zoom), 0)

        # Draw hover/selection highlight
        if hovered is not None:
            hx, hy = hovered
            px, py = tile_to_rotated_px(hx, hy)
            pygame.draw.rect(screen, (255, 255, 0), (px - offset_x, py - offset_y, zoom, zoom), 2)
        if selected is not None:
            sx, sy = selected
            px, py = tile_to_rotated_px(sx, sy)
            pygame.draw.rect(screen, (0, 255, 255), (px - offset_x, py - offset_y, zoom, zoom), 2)

        # Live highlights for server actions
        if "active_highlights" in locals() and active_highlights:
            new_list: List[Tuple[int, int, int]] = []
            for x, y, ttl in active_highlights:
                px, py = tile_to_rotated_px(x, y)
                col = (255, 80, 80)
                pygame.draw.rect(screen, col, (px - offset_x, py - offset_y, zoom, zoom), 0)
                pygame.draw.rect(
                    screen, (255, 220, 220), (px - offset_x, py - offset_y, zoom, zoom), 1
                )
                if ttl - 1 > 0:
                    new_list.append((x, y, ttl - 1))
            active_highlights = new_list

        # Draw info overlay
        ui_font = pygame.font.SysFont(None, 18)
        overlay_lines: List[str] = []

        def append_info(title: str, info: Dict[str, str]):
            overlay_lines.append(title)
            base_keys = ("Tile", "Type", "Height", "Owner")
            for k in base_keys:
                if k in info:
                    overlay_lines.append(f"  {k}: {info[k]}")
            # Extended owner colour if present
            if "OwnerColour" in info:
                overlay_lines.append(f"  OwnerColour: {info['OwnerColour']}")
            # Industry details
            if "IndustryID" in info:
                for k in (
                    "IndustryID",
                    "IndustryType",
                    "IndustryOwner",
                    "IndustryLocation",
                    "Construction",
                    "Anim",
                    "GfxID",
                ):
                    if k in info:
                        overlay_lines.append(f"  {k}: {info[k]}")
            # Raw flags
            if "Flags" in info:
                overlay_lines.append(f"  Flags: {info['Flags']}")
            # Raw m* bytes
            for k in ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"):
                if k in info:
                    overlay_lines.append(f"  {k}: {info[k]}")

        if hovered is not None:
            append_info("Hovered:", get_tile_info(*hovered))
        if selected is not None:
            overlay_lines.append("")
            append_info("Selected:", get_tile_info(*selected))

        if overlay_lines:
            # Background box
            padding = 6
            line_h = 18
            box_w = max(ui_font.size(line)[0] for line in overlay_lines) + padding * 2
            box_h = line_h * len(overlay_lines) + padding * 2
            bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            screen.blit(bg, (8, 8))
            # Text
            y = 8 + padding
            for line in overlay_lines:
                text = ui_font.render(line, True, (230, 230, 230))
                screen.blit(text, (8 + padding, y))
                y += line_h

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
