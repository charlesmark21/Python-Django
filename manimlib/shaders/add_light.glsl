vec4 add_light(vec4 raw_color, vec3 point, vec3 unit_normal, vec3 light_coords, float gloss){
    if(gloss == 0.0) return raw_color;

    // TODO, do we actually want this?  For VMobjects its nice to just choose whichever unit normal
    // is pointing towards the camera.
    if(unit_normal.z < 0){
        unit_normal *= -1;
    }

    float camera_distance = 6;  // TODO, read this in as a uniform?
    // Assume everything has already been rotated such that camera is in the z-direction
    vec3 to_camera = vec3(0, 0, camera_distance) - point;
    vec3 to_light = light_coords - point;
    vec3 light_reflection = -to_light + 2 * unit_normal * dot(to_light, unit_normal);
    float dot_prod = dot(normalize(light_reflection), normalize(to_camera));
    // float shine = gloss * exp(-3 * pow(1 - dot_prod, 2));
    float shine = 2 * gloss * exp(-1 * pow(1 - dot_prod, 2));
    float dp2 = dot(normalize(to_light), unit_normal);
    return vec4(
        mix(0.5, 1.0, max(dp2, 0)) * mix(raw_color.rgb, vec3(1.0), shine),
        raw_color.a
    );
}