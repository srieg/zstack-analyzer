/**
 * WebGL Shaders for Volume Rendering
 * Optimized for Z-stack microscopy visualization
 */

export const volumeVertexShader = `
varying vec3 vPosition;
varying vec3 vNormal;
varying vec3 vWorldPosition;

void main() {
  vPosition = position;
  vNormal = normalMatrix * normal;
  vec4 worldPosition = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPosition.xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

export const volumeFragmentShader = `
precision highp float;
precision highp sampler3D;

uniform sampler3D u_data;
uniform vec3 u_size;
uniform int u_renderMode; // 0=volume, 1=mip, 2=slice, 3=isosurface
uniform float u_threshold;
uniform float u_isoValue;
uniform float u_stepSize;
uniform float u_opacity;
uniform float u_brightness;
uniform float u_contrast;
uniform int u_sliceAxis; // 0=x, 1=y, 2=z
uniform float u_slicePosition;
uniform int u_colorMap;
uniform vec3 u_cameraPosition;

varying vec3 vPosition;
varying vec3 vNormal;
varying vec3 vWorldPosition;

// Color maps
vec3 grayscale(float t) {
  return vec3(t);
}

vec3 hot(float t) {
  float r = clamp(t * 3.0, 0.0, 1.0);
  float g = clamp(t * 3.0 - 1.0, 0.0, 1.0);
  float b = clamp(t * 3.0 - 2.0, 0.0, 1.0);
  return vec3(r, g, b);
}

vec3 cool(float t) {
  return vec3(t, 1.0 - t, 1.0);
}

vec3 viridis(float t) {
  vec3 c0 = vec3(0.267004, 0.004874, 0.329415);
  vec3 c1 = vec3(0.127568, 0.566949, 0.550556);
  vec3 c2 = vec3(0.993248, 0.906157, 0.143936);

  if (t < 0.5) {
    return mix(c0, c1, t * 2.0);
  } else {
    return mix(c1, c2, (t - 0.5) * 2.0);
  }
}

vec3 plasma(float t) {
  vec3 c0 = vec3(0.050383, 0.029803, 0.527975);
  vec3 c1 = vec3(0.808652, 0.289004, 0.388127);
  vec3 c2 = vec3(0.940015, 0.975158, 0.131326);

  if (t < 0.5) {
    return mix(c0, c1, t * 2.0);
  } else {
    return mix(c1, c2, (t - 0.5) * 2.0);
  }
}

vec3 turbo(float t) {
  vec3 c0 = vec3(0.190631, 0.070610, 0.489397);
  vec3 c1 = vec3(0.124870, 0.569265, 0.551229);
  vec3 c2 = vec3(0.988362, 0.998364, 0.644924);

  if (t < 0.5) {
    return mix(c0, c1, t * 2.0);
  } else {
    return mix(c1, c2, (t - 0.5) * 2.0);
  }
}

vec3 applyColorMap(float value, int mapType) {
  if (mapType == 0) return grayscale(value);
  if (mapType == 1) return hot(value);
  if (mapType == 2) return cool(value);
  if (mapType == 3) return viridis(value);
  if (mapType == 4) return plasma(value);
  if (mapType == 5) return turbo(value);
  return grayscale(value);
}

// Apply brightness and contrast
float adjustBrightnessContrast(float value) {
  value = value * u_contrast + u_brightness;
  return clamp(value, 0.0, 1.0);
}

// Sample volume with trilinear interpolation
float sampleVolume(vec3 texCoord) {
  if (texCoord.x < 0.0 || texCoord.x > 1.0 ||
      texCoord.y < 0.0 || texCoord.y > 1.0 ||
      texCoord.z < 0.0 || texCoord.z > 1.0) {
    return 0.0;
  }
  return texture(u_data, texCoord).r;
}

// Compute gradient for shading
vec3 computeGradient(vec3 texCoord) {
  float dx = 1.0 / u_size.x;
  float dy = 1.0 / u_size.y;
  float dz = 1.0 / u_size.z;

  float gx = sampleVolume(texCoord + vec3(dx, 0.0, 0.0)) - sampleVolume(texCoord - vec3(dx, 0.0, 0.0));
  float gy = sampleVolume(texCoord + vec3(0.0, dy, 0.0)) - sampleVolume(texCoord - vec3(0.0, dy, 0.0));
  float gz = sampleVolume(texCoord + vec3(0.0, 0.0, dz)) - sampleVolume(texCoord - vec3(0.0, 0.0, dz));

  return normalize(vec3(gx, gy, gz));
}

void main() {
  vec3 rayOrigin = vWorldPosition;
  vec3 rayDir = normalize(vWorldPosition - u_cameraPosition);

  // Convert to texture coordinates (0-1)
  vec3 texCoord = (vPosition + 1.0) * 0.5;

  // SLICE MODE
  if (u_renderMode == 2) {
    vec3 sliceCoord = texCoord;
    if (u_sliceAxis == 0) sliceCoord.x = u_slicePosition;
    else if (u_sliceAxis == 1) sliceCoord.y = u_slicePosition;
    else sliceCoord.z = u_slicePosition;

    float value = sampleVolume(sliceCoord);
    value = adjustBrightnessContrast(value);

    if (value < u_threshold) discard;

    vec3 color = applyColorMap(value, u_colorMap);
    gl_FragColor = vec4(color, value * u_opacity);
    return;
  }

  // Ray marching setup
  vec3 boxMin = vec3(-1.0);
  vec3 boxMax = vec3(1.0);

  // Ray-box intersection
  vec3 invDir = 1.0 / rayDir;
  vec3 tMin = (boxMin - rayOrigin) * invDir;
  vec3 tMax = (boxMax - rayOrigin) * invDir;
  vec3 t1 = min(tMin, tMax);
  vec3 t2 = max(tMin, tMax);
  float tNear = max(max(t1.x, t1.y), t1.z);
  float tFar = min(min(t2.x, t2.y), t2.z);

  if (tNear > tFar || tFar < 0.0) {
    discard;
  }

  tNear = max(0.0, tNear);

  // Ray marching
  float t = tNear;
  float stepSize = u_stepSize;
  vec4 accumulatedColor = vec4(0.0);
  float maxIntensity = 0.0;

  for (int i = 0; i < 512; i++) {
    if (t > tFar) break;

    vec3 samplePos = rayOrigin + rayDir * t;
    vec3 sampleTexCoord = (samplePos + 1.0) * 0.5;

    float value = sampleVolume(sampleTexCoord);
    value = adjustBrightnessContrast(value);

    // MAXIMUM INTENSITY PROJECTION
    if (u_renderMode == 1) {
      maxIntensity = max(maxIntensity, value);
    }
    // ISOSURFACE
    else if (u_renderMode == 3) {
      if (abs(value - u_isoValue) < 0.02) {
        vec3 gradient = computeGradient(sampleTexCoord);
        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        float diffuse = max(dot(gradient, lightDir), 0.0);
        float ambient = 0.3;
        float lighting = ambient + diffuse * 0.7;

        vec3 color = applyColorMap(value, u_colorMap);
        gl_FragColor = vec4(color * lighting, 1.0);
        return;
      }
    }
    // VOLUME RENDERING
    else {
      if (value > u_threshold) {
        vec3 color = applyColorMap(value, u_colorMap);
        float alpha = value * u_opacity;

        // Front-to-back compositing
        accumulatedColor.rgb += (1.0 - accumulatedColor.a) * color * alpha;
        accumulatedColor.a += (1.0 - accumulatedColor.a) * alpha;

        // Early ray termination
        if (accumulatedColor.a > 0.95) break;
      }
    }

    t += stepSize;
  }

  if (u_renderMode == 1) {
    // MIP output
    vec3 color = applyColorMap(maxIntensity, u_colorMap);
    gl_FragColor = vec4(color, maxIntensity);
  } else {
    // Volume rendering output
    gl_FragColor = accumulatedColor;
  }

  if (gl_FragColor.a < 0.01) discard;
}
`;

export const sliceVertexShader = `
varying vec2 vUv;
varying vec3 vPosition;

void main() {
  vUv = uv;
  vPosition = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

export const sliceFragmentShader = `
precision highp float;
precision highp sampler3D;

uniform sampler3D u_data;
uniform int u_axis;
uniform float u_position;
uniform float u_opacity;
uniform float u_brightness;
uniform float u_contrast;
uniform int u_colorMap;

varying vec2 vUv;
varying vec3 vPosition;

vec3 grayscale(float t) { return vec3(t); }
vec3 hot(float t) {
  float r = clamp(t * 3.0, 0.0, 1.0);
  float g = clamp(t * 3.0 - 1.0, 0.0, 1.0);
  float b = clamp(t * 3.0 - 2.0, 0.0, 1.0);
  return vec3(r, g, b);
}
vec3 viridis(float t) {
  vec3 c0 = vec3(0.267004, 0.004874, 0.329415);
  vec3 c1 = vec3(0.127568, 0.566949, 0.550556);
  vec3 c2 = vec3(0.993248, 0.906157, 0.143936);
  return t < 0.5 ? mix(c0, c1, t * 2.0) : mix(c1, c2, (t - 0.5) * 2.0);
}

vec3 applyColorMap(float value, int mapType) {
  if (mapType == 0) return grayscale(value);
  if (mapType == 1) return hot(value);
  if (mapType == 3) return viridis(value);
  return grayscale(value);
}

void main() {
  vec3 texCoord;

  if (u_axis == 0) {
    texCoord = vec3(u_position, vUv.x, vUv.y);
  } else if (u_axis == 1) {
    texCoord = vec3(vUv.x, u_position, vUv.y);
  } else {
    texCoord = vec3(vUv.x, vUv.y, u_position);
  }

  float value = texture(u_data, texCoord).r;
  value = value * u_contrast + u_brightness;
  value = clamp(value, 0.0, 1.0);

  vec3 color = applyColorMap(value, u_colorMap);
  gl_FragColor = vec4(color, value * u_opacity);
}
`;
