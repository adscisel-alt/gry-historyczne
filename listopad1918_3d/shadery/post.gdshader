// Fotografia z 1918 r.: sepia z luminancji, ziarno, rysy kliszy, winieta, migotanie.
// Wyjątek: fiolet (kaptur Damiana) zostaje w kolorze.
shader_type canvas_item;

uniform sampler2D ekran : hint_screen_texture, filter_linear_mipmap;
uniform float ziarno = 0.07;
uniform float winieta = 0.5;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec3 c = texture(ekran, SCREEN_UV).rgb;
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	l = clamp((l - 0.03) * 1.12, 0.0, 1.0);
	vec3 sepia = mix(vec3(0.12, 0.08, 0.05), vec3(0.96, 0.90, 0.78), l);
	float mx = max(c.r, max(c.g, c.b));
	float mn = min(c.r, min(c.g, c.b));
	float sat = mx > 0.001 ? (mx - mn) / mx : 0.0;
	float fiolet = step(0.3, sat) * step(c.g + 0.06, c.b) * step(c.g + 0.02, c.r);
	vec3 wyn = mix(sepia, mix(sepia, c * 1.1, 0.85), fiolet);
	float t = floor(TIME * 18.0);
	float n = hash(SCREEN_UV * vec2(1280.0, 720.0) + t * 17.0);
	wyn += (n - 0.5) * ziarno;
	// rysa kliszy co jakiś czas
	float rx = hash(vec2(t, 3.0));
	float rysa = step(0.93, hash(vec2(t, 7.0))) * smoothstep(0.0015, 0.0, abs(SCREEN_UV.x - rx));
	wyn = mix(wyn, vec3(0.97, 0.93, 0.85), rysa * 0.6);
	vec2 d = (SCREEN_UV - 0.5) * vec2(1.0, 0.85);
	float v = smoothstep(0.80, 0.30, length(d));
	wyn *= mix(1.0 - winieta, 1.0, v);
	wyn *= 0.97 + 0.03 * hash(vec2(t, 1.0));
	COLOR = vec4(wyn, 1.0);
}
