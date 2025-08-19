import math
import pybirdsreynolds.const as const
import random 

birds = []
velocities = []

def limit_speed(vx, vy):
    speed = math.sqrt(vx*vx + vy*vy)
    if speed > const.MAX_SPEED:
        vx = (vx / speed) * const.MAX_SPEED
        vy = (vy / speed) * const.MAX_SPEED
    return vx, vy



def generate_points_and_facultative_move(pbirds, pvelocities, with_move, translate):
    if not pbirds or pbirds==[]: 
        for _ in range(const.NUM_BIRDS):
            px = random.randint(const.MARGIN + const.WIDTH_CONTROLS, const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS)
            py = random.randint(const.MARGIN, const.HEIGHT - const.MARGIN)
            pbirds.append((px, py))
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0, const.MAX_SPEED)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            pvelocities.append((vx, vy))
    else:
        if translate:
            for i in range(len(pbirds)):
                x, y = pbirds[i]
                if const.HIDDEN:
                    pbirds[i] = (x + const.WIDTH_CONTROLS_DEFAULT, y)
                else:
                    pbirds[i] = (x - const.WIDTH_CONTROLS_DEFAULT, y)                               
        # Keep birds only if inside
        inside_points = []
        inside_velocities = []
        for (x, y), (vx, vy) in zip(pbirds, pvelocities):
            if const.WIDTH_CONTROLS + const.MARGIN <= x <= const.WIDTH_CONTROLS + const.WIDTH - const.MARGIN and 0 + const.MARGIN <= y <= const.HEIGHT - const.MARGIN:
                inside_points.append((x, y))
                inside_velocities.append((vx, vy))
        pbirds[:] = inside_points
        pvelocities[:] = inside_velocities
        current_count = len(pbirds)
        
        # Add birds if not enough
        if const.NUM_BIRDS > current_count:
            for _ in range(const.NUM_BIRDS - current_count):
                px = random.randint(const.MARGIN + const.WIDTH_CONTROLS, const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS)
                py = random.randint(const.MARGIN, const.HEIGHT - const.MARGIN)
                pbirds.append((px, py))

                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, const.MAX_SPEED)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                pvelocities.append((vx, vy))

        # Delete birds if not enough
        elif const.NUM_BIRDS < current_count:
            for _ in range(current_count - const.NUM_BIRDS):
                idx = random.randint(0, len(pbirds) - 1)
                pbirds.pop(idx)
                pvelocities.pop(idx)

        if with_move:                    
            new_velocities=[]
            #TODO n2 use Grid / Uniform Cell List 
            for i, (x, y) in enumerate(pbirds):
                move_sep_x, move_sep_y = 0, 0
                move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = 0, 0, 0, 0
                move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
                neighbors = 0
                vx, vy = pvelocities[i]
                if const.NEIGHBOR_RADIUS > 0 and not (const.SEP_WEIGHT == 0 and const.ALIGN_WEIGHT == 0 and const.COH_WEIGHT == 0):
                    for j, (x2, y2) in enumerate(pbirds):
                        if i == j:
                            continue
                        dist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
                        if dist < const.NEIGHBOR_RADIUS and dist > 0:
                            # SEPARATION
                            # If a neighbor is too close, add a vector to move away from it (opposite direction of the neighbor).
                            move_sep_x += (x - x2) / dist
                            move_sep_y += (y - y2) / dist
                            # ALIGNMENT
                            # Add the neighbor's velocity so the bird tends to align with it.
                            # Division is done later
                            vx2, vy2 = pvelocities[j]
                            move_align_x_tmp += vx2
                            move_align_y_tmp += vy2
                            # COHESION
                            # Add the neighbor's position to later calculate an average point, 
                            # so the bird moves toward the group's center.
                            # Division is done later
                            move_coh_x_tmp += x2
                            move_coh_y_tmp += y2
                            neighbors += 1
                    
                    if neighbors > 0:
                        move_align_x = move_align_x_tmp/neighbors
                        move_align_y = move_align_y_tmp/neighbors
                        move_coh_x = move_coh_x_tmp/neighbors
                        move_coh_y = move_coh_y_tmp/neighbors
                        move_coh_x = move_coh_x - x
                        move_coh_y = move_coh_y - y

                    vx += const.SEP_WEIGHT * move_sep_x + const.ALIGN_WEIGHT * move_align_x + const.COH_WEIGHT * move_coh_x
                    vy += const.SEP_WEIGHT * move_sep_y + const.ALIGN_WEIGHT * move_align_y + const.COH_WEIGHT * move_coh_y
            
                #RANDOM
                speed = math.sqrt(vx**2 + vy**2)
                if const.RANDOM_SPEED!=0:
                    target_speed = const.MAX_SPEED / 2
                    sigma_percent = const.RANDOM_SPEED   
                    adjust_strength = 0.05 
                    sigma_base = (sigma_percent / 100) * const.MAX_SPEED
                    weight = 4 * speed * (const.MAX_SPEED - speed) / (const.MAX_SPEED ** 2)
                    sigma = sigma_base * weight
                    delta_speed = random.gauss(0, sigma)
                    new_speed = speed + delta_speed
                    new_speed += (target_speed - new_speed) * adjust_strength
                    new_speed = max(0.1, min(const.MAX_SPEED, new_speed))
                    factor = new_speed / speed
                    vx *= factor
                    vy *= factor
                if const.RANDOM_ANGLE!=0:
                    angle = math.atan2(vy, vx)
                    angle += math.radians(random.uniform(-1 * const.RANDOM_ANGLE, const.RANDOM_ANGLE))
                    speed = math.sqrt(vx**2 + vy**2)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                vx, vy = limit_speed(vx, vy)
                    
                new_velocities.append((vx, vy))

            # Update positions
            new_points = []
            for (x, y), (vx, vy) in zip(pbirds, new_velocities):
                nx = x + vx
                ny = y + vy
                # Bounces
                while nx < const.MARGIN + const.WIDTH_CONTROLS or nx > const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS:
                    if nx < const.MARGIN + const.WIDTH_CONTROLS:
                        overshoot = (const.MARGIN + const.WIDTH_CONTROLS) - nx
                        nx = (const.MARGIN + const.WIDTH_CONTROLS) + overshoot
                        vx = abs(vx)
                    elif nx > const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS:
                        overshoot = nx - (const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS)
                        nx = (const.WIDTH - const.MARGIN + const.WIDTH_CONTROLS) - overshoot
                        vx = -abs(vx)
                while ny < const.MARGIN or ny > const.HEIGHT - const.MARGIN:
                    if ny < const.MARGIN:
                        overshoot = const.MARGIN - ny
                        ny = const.MARGIN + overshoot
                        vy = abs(vy)
                    elif ny > const.HEIGHT - const.MARGIN:
                        overshoot = ny - (const.HEIGHT - const.MARGIN)
                        ny = (const.HEIGHT - const.MARGIN) - overshoot
                        vy = -abs(vy)
                idx = pbirds.index((x, y))
                pvelocities[idx] = (vx, vy)
                new_points.append((nx, ny))
            pbirds[:] = new_points
