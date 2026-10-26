import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";
import { RGBELoader } from "three/addons/loaders/RGBELoader.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { GTAOPass } from "three/addons/postprocessing/GTAOPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const EYE = 5.5, RADIUS = 1.1, WALK_SPEED = 4.5;       // feet, feet/sec
const SPAWN = { basement: [40, 18, 90], main: [21, 5, 0], upper: [30, 16, 0] }; // x, y, heading deg (0 = north)
const COLORS = { wallExt: 0xe7e1d3, wallInt: 0xf4f1ea, doorExt: 0x24282d, garageDoor: 0xc3c6ca,
  trim: 0xf7f6f2, door: 0xf4f3ef, ceiling: 0xf8f7f3, soffit: 0xf2f0ea };

const isTouch = matchMedia("(pointer: coarse)").matches;
const $ = (s) => document.querySelector(s);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfd6e6);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8478, 1.1));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const sun = new THREE.DirectionalLight(0xfff4e5, 2.2);     // afternoon sun from the south-west
sun.target.position.set(47, 0, -31);
sun.position.set(47 - 45, 85, -31 + 60);
sun.castShadow = true;
sun.shadow.mapSize.set(isTouch ? 2048 : 4096, isTouch ? 2048 : 4096);
Object.assign(sun.shadow.camera, { left: -75, right: 75, top: 75, bottom: -75, near: 10, far: 250 });
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.04; sun.shadow.radius = 3;
scene.add(sun, sun.target);
// ground with a hole over the stairwell (the only place the house opens down to the basement)
const groundShape = new THREE.Shape().setFromPoints([[-253, -269], [347, -269], [347, 331], [-253, 331]].map(([x, y]) => new THREE.Vector2(x, y)));
groundShape.holes.push(new THREE.Path().setFromPoints([[28, 0], [28, 14], [38, 14], [38, 0]].map(([x, y]) => new THREE.Vector2(x, y))));
const ground = new THREE.Mesh(new THREE.ShapeGeometry(groundShape),
  new THREE.MeshStandardMaterial({ color: 0x8fae6e, roughness: 1 }));   // grass map attached below
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.02; ground.receiveShadow = true;   // shape xy = house xy
scene.add(ground);

const cam = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.1, 800);
const orbit = new OrbitControls(cam, renderer.domElement);
orbit.target.set(47, 5, -31);
orbit.enableDamping = true;

// soft sky/ground environment so gloss, metal and mirrors have something to reflect
{
  const envScene = new THREE.Scene(), geo = new THREE.SphereGeometry(50, 32, 16), col = [];
  for (let i = 0; i < geo.attributes.position.count; i++) {
    const t = geo.attributes.position.getY(i) / 50;
    const c = new THREE.Color(t > 0 ? 0xf2f4f6 : 0x9c9284).lerp(new THREE.Color(0xd8d4cc), 1 - Math.abs(t));
    col.push(c.r, c.g, c.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  envScene.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide })));
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(envScene, 0.04).texture;
}
// real sky HDRI (Poly Haven, CC0) replaces the placeholder environment once it arrives
new RGBELoader().load("./vendor/hdri/sky_1k.hdr", (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = new THREE.PMREMGenerator(renderer).fromEquirectangular(hdr).texture;
  scene.background = hdr; scene.backgroundIntensity = 0.9;
});

// ---------- procedural textures (world-scaled: `size` = feet covered by one tile) ----------
function rng(seed) { return () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646; }
function canvasTex(size, draw, px = 512) {
  const cv = document.createElement("canvas"); cv.width = cv.height = px;
  draw(cv.getContext("2d"), px);
  const t = new THREE.CanvasTexture(cv);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  t.repeat.set(1 / size, 1 / size); t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return t;
}
function grain(g, x, y, w, h, r, n = 6) {
  for (let i = 0; i < n; i++) {
    g.strokeStyle = `rgba(60,35,15,${0.05 + r() * 0.08})`; g.lineWidth = 0.6 + r() * 1.2;
    const yy = y + r() * h; g.beginPath(); g.moveTo(x, yy);
    for (let xx = x; xx <= x + w; xx += 24) g.lineTo(xx, yy + Math.sin(xx * 0.02 + i) * 1.5);
    g.stroke();
  }
}
const TEX = {
  hardwood: () => canvasTex(4, (g, P) => {       // 5" white-oak planks, staggered joints
    const r = rng(7), rows = 10, rh = P / rows;
    for (let row = 0; row < rows; row++) {
      let x = -r() * P;
      while (x < P) {
        const len = P * (0.35 + r() * 0.6), tone = r();
        g.fillStyle = `hsl(${31 + tone * 4}, ${36 + tone * 6}%, ${52 + tone * 6}%)`;
        for (const off of [0, P]) {
          g.fillRect(x + off, row * rh, len, rh);
          grain(g, x + off, row * rh, len, rh, r, 5);
          g.fillStyle = "rgba(50,30,15,.55)"; g.fillRect(x + off + len - 1.5, row * rh, 1.5, rh);
          g.fillStyle = `hsl(${31 + tone * 4}, ${36 + tone * 6}%, ${52 + tone * 6}%)`;
        }
        x += len;
      }
      g.fillStyle = "rgba(50,30,15,.5)"; g.fillRect(0, row * rh, P, 1.2);
    }
  }),
  wood: () => canvasTex(3, (g, P) => {
    g.fillStyle = "#fff"; g.fillRect(0, 0, P, P); const r = rng(3);
    for (let k = 0; k < 8; k++) grain(g, 0, k * P / 8, P, P / 8, r, 10);
  }),
  tile: () => canvasTex(2, (g, P) => {           // 6x3 subway, offset rows
    g.fillStyle = "#b9b5ad"; g.fillRect(0, 0, P, P);
    const tw = P / 4, th = P / 8, r = rng(5);
    for (let row = 0; row < 8; row++) for (let i = -1; i < 5; i++) {
      const v = 245 + r() * 10; g.fillStyle = `rgb(${v},${v},${v - 3})`;
      g.fillRect(i * tw + (row % 2) * tw / 2 + 2, row * th + 2, tw - 4, th - 4);
    }
  }),
  fabric: () => canvasTex(1.5, (g, P) => {
    const d = g.createImageData(P, P), r = rng(11);
    for (let i = 0; i < d.data.length; i += 4) {
      const v = 228 + r() * 27 - ((i / 4) % 3 === 0 ? 10 : 0);
      d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255;
    }
    g.putImageData(d, 0, 0);
  }, 256),
  concrete: () => canvasTex(8, (g, P) => {
    const r = rng(13); g.fillStyle = "#c9c7c2"; g.fillRect(0, 0, P, P);
    for (let i = 0; i < 900; i++) {
      g.fillStyle = `rgba(${r() < 0.5 ? "90,90,88" : "240,240,236"},${r() * 0.08})`;
      g.beginPath(); g.arc(r() * P, r() * P, 2 + r() * 30, 0, 7); g.fill();
    }
  }),
  floorTile: () => canvasTex(4, (g, P) => {      // 12x24 porcelain, warm gray, 1/3 offset
    g.fillStyle = "#a7a198"; g.fillRect(0, 0, P, P); const r = rng(23), tw = P / 2, th = P / 4;
    for (let row = 0; row < 4; row++) for (let i = -1; i < 3; i++) {
      const v = r(); g.fillStyle = `hsl(36, ${6 + v * 4}%, ${80 + v * 5}%)`;
      g.fillRect(i * tw + (row % 3) * tw / 3 + 1.5, row * th + 1.5, tw - 3, th - 3);
    }
  }),
  siding: () => canvasTex(4, (g, P) => {         // board-and-batten: 12" boards, 2.5" battens every 16"
    g.fillStyle = "#f4f2ec"; g.fillRect(0, 0, P, P); const r = rng(29), bw = P / 3;
    for (let i = 0; i < 3; i++) {
      const x = i * bw;
      g.fillStyle = "rgba(0,0,0,.10)"; g.fillRect(x + bw * 0.16, 0, 3, P);             // batten shadow
      g.fillStyle = "#fbfaf6"; g.fillRect(x, 0, bw * 0.16, P);                          // batten face
      g.fillStyle = "rgba(255,255,255,.6)"; g.fillRect(x, 0, 2, P);
      for (let k = 0; k < 40; k++) { g.fillStyle = `rgba(0,0,0,${r() * 0.025})`; g.fillRect(x + r() * bw, r() * P, 1, 20 + r() * 60); }
    }
  }),
  stone: () => canvasTex(3, (g, P) => {          // ledgestone, warm grays
    g.fillStyle = "#6f675e"; g.fillRect(0, 0, P, P); const r = rng(31);
    let y = 0;
    while (y < P) {
      const h = 18 + r() * 26; let x = -r() * 80;
      while (x < P) {
        const w = 50 + r() * 140, v = r();
        g.fillStyle = `hsl(${28 + v * 14}, ${8 + v * 10}%, ${52 + v * 20}%)`;
        for (const off of [0, P]) g.fillRect(x - off + 2, y + 2, w - 4, h - 4);
        x += w;
      }
      y += h;
    }
  }),
  shingle: () => canvasTex(3, (g, P) => {        // architectural asphalt, ~5.5" exposure, staggered tabs
    g.fillStyle = "#2c2e31"; g.fillRect(0, 0, P, P); const r = rng(37), rows = 6, rh = P / rows;
    for (let row = 0; row < rows; row++) {
      let x = -r() * 60;
      while (x < P) {
        const w = 25 + r() * 60, v = r();
        g.fillStyle = `hsl(210, 3%, ${22 + v * 14}%)`;
        for (const off of [0, P]) g.fillRect(x - off, row * rh, w - 2, rh - 3);
        x += w;
      }
      g.fillStyle = "rgba(0,0,0,.55)"; g.fillRect(0, row * rh + rh - 4, P, 4);
    }
    const d = g.getImageData(0, 0, P, P);
    for (let i = 0; i < d.data.length; i += 4) { const n = (r() - 0.5) * 22; d.data[i] += n; d.data[i + 1] += n; d.data[i + 2] += n; }
    g.putImageData(d, 0, 0);
  }),
  metalRoof: () => canvasTex(4, (g, P) => {      // standing seam every 16"
    g.fillStyle = "#3a3d41"; g.fillRect(0, 0, P, P);
    for (let i = 0; i < 3; i++) {
      const x = i * P / 3;
      g.fillStyle = "#55595e"; g.fillRect(x, 0, 4, P);
      g.fillStyle = "rgba(0,0,0,.35)"; g.fillRect(x + 4, 0, 4, P);
    }
  }),
  grass: () => canvasTex(10, (g, P) => {
    g.fillStyle = "#7f9f5f"; g.fillRect(0, 0, P, P); const r = rng(41);
    for (let i = 0; i < 9000; i++) {
      const v = r(); g.fillStyle = `hsl(${85 + v * 25}, ${30 + v * 20}%, ${32 + v * 22}%)`;
      g.fillRect(r() * P, r() * P, 1.5, 3 + r() * 4);
    }
  }),
  garageDoor: () => canvasTex(8, (g, P) => {     // 4 raised sections, glass top row
    g.fillStyle = "#eceae4"; g.fillRect(0, 0, P, P); const sh = P / 4;
    for (let k = 0; k < 4; k++) {
      g.fillStyle = "rgba(0,0,0,.35)"; g.fillRect(0, k * sh, P, 3);
      if (k === 0) for (let i = 0; i < 4; i++) { g.fillStyle = "#30353b"; g.fillRect(i * P / 4 + 10, 18, P / 4 - 20, sh - 36); }
      else for (let i = 0; i < 4; i++) { g.strokeStyle = "rgba(0,0,0,.18)"; g.lineWidth = 3; g.strokeRect(i * P / 4 + 10, k * sh + 14, P / 4 - 20, sh - 28); }
    }
  }),
  rubber: () => canvasTex(4, (g, P) => {
    g.fillStyle = "#2a2b2d"; g.fillRect(0, 0, P, P); const r = rng(17);
    for (let i = 0; i < 2500; i++) { g.fillStyle = r() < 0.5 ? "#4a4c50" : "#1c1c1e"; g.fillRect(r() * P, r() * P, 2, 2); }
    g.strokeStyle = "#151516"; g.lineWidth = 2; g.strokeRect(0, 0, P, P);   // 4' mats
  }),
  pavers: () => canvasTex(6, (g, P) => {         // 2' x 3' bluestone-ish pavers
    g.fillStyle = "#77736c"; g.fillRect(0, 0, P, P); const r = rng(19), s = P / 6;
    for (let row = 0; row < 3; row++) for (let i = 0; i < 2; i++) {
      const v = r(); g.fillStyle = `hsl(${30 + v * 20}, ${8 + v * 8}%, ${58 + v * 12}%)`;
      g.fillRect(i * 3 * s + 3, row * 2 * s + 3, 3 * s - 6, 2 * s - 6);
    }
  }),
};
const texCache = {};
const tex = (k) => (texCache[k] ??= TEX[k]());

const mats = {};
function mat(name) {
  if (mats[name]) return mats[name];
  const [kind, hex] = name.includes(":") ? name.split(":") : [name, null];
  const S = (o) => new THREE.MeshStandardMaterial({ envMapIntensity: 0.6, ...o });
  const m = {
    glass: () => S({ color: 0xbfe3f0, transparent: true, opacity: 0.28, roughness: 0.05, metalness: 0.1, depthWrite: false }),
    mirror: () => S({ color: 0xe8eef2, roughness: 0.03, metalness: 1 }),
    hardwood: () => S({ color: 0xffffff, map: tex("hardwood"), roughness: 0.45 }),
    stair: () => S({ color: 0xffffff, map: tex("hardwood"), roughness: 0.45 }),
    concrete: () => S({ color: 0xffffff, map: tex("concrete"), roughness: 0.85 }),
    rubber: () => S({ color: 0xffffff, map: tex("rubber"), roughness: 0.95 }),
    pavers: () => S({ color: 0xffffff, map: tex("pavers"), roughness: 0.9 }),
    paint: () => S({ color: hex, roughness: 0.9 }),
    fix: () => S({ color: hex, roughness: 0.75 }),
    gloss: () => S({ color: hex, roughness: 0.22 }),
    metal: () => S({ color: hex, roughness: 0.3, metalness: 0.85 }),
    wood: () => S({ color: hex, map: tex("wood"), roughness: 0.55 }),
    fabric: () => S({ color: hex, map: tex("fabric"), roughness: 1 }),
    tile: () => S({ color: hex, map: tex("tile"), roughness: 0.25 }),
    floorTile: () => S({ color: 0xffffff, map: tex("floorTile"), roughness: 0.35 }),
    siding: () => S({ color: 0xffffff, map: tex("siding"), roughness: 0.8 }),
    stone: () => S({ color: 0xffffff, map: tex("stone"), roughness: 0.95 }),
    shingle: () => S({ color: 0xffffff, map: tex("shingle"), roughness: 0.9 }),
    metalRoof: () => S({ color: 0xb0b4b8, map: tex("metalRoof"), roughness: 0.55, metalness: 0.25, envMapIntensity: 0.35 }),
    garageDoor: () => S({ color: 0xffffff, map: tex("garageDoor"), roughness: 0.6 }),
    frame: () => S({ color: 0x1d1f22, roughness: 0.4, metalness: 0.2 }),
    lamp: () => S({ color: hex, emissive: hex, emissiveIntensity: 1.3 }),
    ceiling: () => S({ color: 0xf8f7f3, emissive: 0x9a978f, roughness: 1 }),   // faces away from sky light
  }[kind];
  return (mats[name] = m ? m() : S({ color: COLORS[name] ?? 0xcccccc, roughness: 0.85 }));
}

// Merge every box of one material on one level into a single mesh (thousands of boxes -> ~60 draws).
// UVs are world-planar in feet so textures keep real scale on every face.
function boxesToGeometry(list) {
  const pos = [], nor = [], uv = [], idx = [];
  for (const [x, y, z, w, d, h] of list) {
    const x0 = x, x1 = x + w, y0 = z, y1 = z + h, z0 = -(y + d), z1 = -y;
    const faces = [   // origin, u edge, v edge, normal, uv axes
      [[x1, y0, z1], [0, 0, z0 - z1], [0, h, 0], [1, 0, 0], [2, 1]],
      [[x0, y0, z0], [0, 0, z1 - z0], [0, h, 0], [-1, 0, 0], [2, 1]],
      [[x0, y1, z1], [w, 0, 0], [0, 0, z0 - z1], [0, 1, 0], [0, 2]],
      [[x0, y0, z0], [w, 0, 0], [0, 0, z1 - z0], [0, -1, 0], [0, 2]],
      [[x0, y0, z1], [w, 0, 0], [0, h, 0], [0, 0, 1], [0, 1]],
      [[x1, y0, z0], [-w, 0, 0], [0, h, 0], [0, 0, -1], [0, 1]],
    ];
    for (const [o, u, v, n, [a, b]] of faces) {
      const base = pos.length / 3;
      for (const [s, t] of [[0, 0], [1, 0], [1, 1], [0, 1]]) {
        const p = [o[0] + u[0] * s + v[0] * t, o[1] + u[1] * s + v[1] * t, o[2] + u[2] * s + v[2] * t];
        pos.push(...p); nor.push(...n); uv.push(p[a], p[b]);
      }
      idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

// Sloped / organic geometry (roofs, gable ends, plants): flat-shaded triangles, double-sided,
// UVs projected on each face's own plane (u = horizontal along the face, v = up the face) in feet.
function polysToGeometry(list) {
  const pos = [], nor = [], uv = [], up = new THREE.Vector3(0, 1, 0);
  for (const flat of list) {
    const P = [];
    for (let i = 0; i < flat.length; i += 3) P.push(new THREE.Vector3(flat[i], flat[i + 2], -flat[i + 1]));
    const n = new THREE.Vector3().subVectors(P[1], P[0]).cross(new THREE.Vector3().subVectors(P[2], P[0])).normalize();
    const u = Math.abs(n.y) > 0.99 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3().crossVectors(up, n).normalize();
    const v = new THREE.Vector3().crossVectors(n, u);
    for (let k = 1; k < P.length - 1; k++) for (const p of [P[0], P[k], P[k + 1]]) {
      pos.push(p.x, p.y, p.z); nor.push(n.x, n.y, n.z); uv.push(p.dot(u), p.dot(v));
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  return g;
}
function matDouble(name) {
  const key = name + "|2";
  if (!mats[key]) { mats[key] = mat(name).clone(); mats[key].side = THREE.DoubleSide; }
  return mats[key];
}
ground.material.map = tex("grass"); ground.material.color.set(0xffffff); ground.material.needsUpdate = true;

const model = await (await fetch("./model.json")).json();
const levelGroups = {}, colliders = [], ceilings = [];
for (const [lvl, L] of Object.entries(model.levels)) {
  const g = new THREE.Group(), byMat = {};
  for (const b of L.boxes) {
    const [x, y, z, w, d, h, m, c] = b;
    (byMat[m] ??= []).push(b);
    if (c) colliders.push({ x0: x, x1: x + w, y0: y, y1: y + d, z0: z, z1: z + h });
  }
  for (const [m, list] of Object.entries(byMat)) {
    if (m === "block") continue;                       // invisible collider (stair openings)
    const mesh = new THREE.Mesh(boxesToGeometry(list), mat(m));
    mesh.castShadow = m !== "glass" && !m.startsWith("lamp:");
    mesh.receiveShadow = true;
    if (m === "glass") mesh.renderOrder = 1;
    if (m === "ceiling") ceilings.push(mesh);
    g.add(mesh);
  }
  const polyByMat = {};
  for (const [m, pts] of L.polys ?? []) (polyByMat[m] ??= []).push(pts);
  for (const [m, list] of Object.entries(polyByMat)) {
    const mesh = new THREE.Mesh(polysToGeometry(list), matDouble(m));
    mesh.castShadow = mesh.receiveShadow = true;
    g.add(mesh);
  }
  levelGroups[lvl] = g; scene.add(g);
}

// room labels (dollhouse only)
const labels = new THREE.Group(); scene.add(labels);
for (const r of model.rooms) {
  const cv = document.createElement("canvas"); cv.width = 256; cv.height = 64;
  const ctx = cv.getContext("2d");
  ctx.font = "bold 30px system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.lineWidth = 6; ctx.strokeStyle = "#000c"; ctx.strokeText(r.name, 128, 32);
  ctx.fillStyle = "#fff"; ctx.fillText(r.name, 128, 32);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), depthTest: false, transparent: true }));
  sp.scale.set(10, 2.5, 1);
  sp.position.set(r.x, model.levels[r.level].elev + 1.5, -r.y);
  sp.userData.level = r.level; sp.renderOrder = 10;
  labels.add(sp);
}

// ---------- state ----------
let mode = "walk", level = "main";
const me = { x: 0, y: 0, yaw: 0, pitch: 0 };   // yaw 0 = looking north (+y house)
function teleport(lvl, x, y, heading) {
  level = lvl; me.x = x; me.y = y; me.yaw = (heading ?? 0) * Math.PI / 180; me.pitch = 0;
  for (const [k, g] of Object.entries(levelGroups)) g.visible = true;
  document.querySelectorAll("[data-lvl]").forEach((b) => b.classList.toggle("on", b.dataset.lvl === lvl));
}
function placeCamera() {
  cam.position.set(me.x, model.levels[level].elev + EYE, -me.y);
  cam.rotation.order = "YXZ";
  cam.rotation.set(me.pitch, -me.yaw, 0);
}
function collide() {
  const z = model.levels[level].elev;
  for (let pass = 0; pass < 3; pass++) {
    for (const b of colliders) {
      if (b.z1 < z + 0.6 || b.z0 > z + 4.5) continue;
      const cx = Math.max(b.x0, Math.min(me.x, b.x1)), cy = Math.max(b.y0, Math.min(me.y, b.y1));
      const dx = me.x - cx, dy = me.y - cy, d2 = dx * dx + dy * dy;
      if (d2 < RADIUS * RADIUS) {
        if (d2 > 1e-8) { const d = Math.sqrt(d2), k = (RADIUS - d) / d; me.x += dx * k; me.y += dy * k; }
        else {   // spawned inside a box: exit through the nearest face
          const out = [[me.x - b.x0, -1, 0], [b.x1 - me.x, 1, 0], [me.y - b.y0, 0, -1], [b.y1 - me.y, 0, 1]]
            .sort((p, q) => p[0] - q[0])[0];
          me.x += out[1] * (out[0] + RADIUS); me.y += out[2] * (out[0] + RADIUS);
        }
      }
    }
  }
}

// ---------- input ----------
const keys = new Set();
addEventListener("keydown", (e) => keys.add(e.code));
addEventListener("keyup", (e) => keys.delete(e.code));
const stick = $("#stick"), nub = $("#nub");
const move = { x: 0, y: 0 };
let stickId = null, lookId = null, lastLook = null, stickC = null;
function lookDelta(dx, dy) { me.yaw += dx * 0.005; me.pitch = Math.max(-1.2, Math.min(1.2, me.pitch - dy * 0.005)); }
const cvs = renderer.domElement;
cvs.addEventListener("touchstart", (e) => {
  if (mode !== "walk") return;
  for (const t of e.changedTouches) {
    if (t.clientX < innerWidth / 2 && stickId === null) {
      stickId = t.identifier; stickC = [t.clientX, t.clientY];
      stick.style.left = t.clientX - 55 + "px"; stick.style.top = t.clientY - 55 + "px"; stick.style.bottom = "auto";
    } else if (lookId === null) { lookId = t.identifier; lastLook = [t.clientX, t.clientY]; }
  }
  e.preventDefault();
}, { passive: false });
cvs.addEventListener("touchmove", (e) => {
  for (const t of e.changedTouches) {
    if (t.identifier === stickId) {
      let dx = t.clientX - stickC[0], dy = t.clientY - stickC[1];
      const m = Math.hypot(dx, dy), max = 50;
      if (m > max) { dx *= max / m; dy *= max / m; }
      move.x = dx / max; move.y = -dy / max;
      nub.style.transform = `translate(${dx}px, ${dy}px)`;
    } else if (t.identifier === lookId) {
      lookDelta(t.clientX - lastLook[0], t.clientY - lastLook[1]); lastLook = [t.clientX, t.clientY];
    }
  }
  e.preventDefault();
}, { passive: false });
const endTouch = (e) => {
  for (const t of e.changedTouches) {
    if (t.identifier === stickId) { stickId = null; move.x = move.y = 0; nub.style.transform = ""; }
    if (t.identifier === lookId) lookId = null;
  }
};
cvs.addEventListener("touchend", endTouch); cvs.addEventListener("touchcancel", endTouch);
let drag = false;
cvs.addEventListener("mousedown", () => { if (mode === "walk") drag = true; });
addEventListener("mouseup", () => (drag = false));
addEventListener("mousemove", (e) => { if (drag && mode === "walk") lookDelta(e.movementX, e.movementY); });

// ---------- UI ----------
const jump = $("#jump");
for (const r of model.rooms) {
  const o = document.createElement("option");
  o.value = JSON.stringify([r.level, r.x, r.y]);
  o.textContent = `${r.name} (${r.level})`; jump.append(o);
}
jump.onchange = () => {
  if (!jump.value) return;
  const [l, x, y] = JSON.parse(jump.value); teleport(l, x, y, me.yaw * 180 / Math.PI); jump.value = "";
};
document.querySelectorAll("[data-lvl]").forEach((b) => (b.onclick = () => { const s = SPAWN[b.dataset.lvl]; teleport(b.dataset.lvl, s[0], s[1], s[2]); }));
// Dollhouse: with the roof on it's an exterior view (solid ground, no labels); with the roof off you
// look into the rooms (see-through ground so the basement shows, room labels on).
function syncDoll() {
  const inside = mode === "doll" && !levelGroups.roof.visible;
  ground.material.transparent = inside; ground.material.opacity = inside ? 0.3 : 1;
  ground.material.depthWrite = !inside; ground.material.needsUpdate = true;
  labels.visible = inside;
  labels.children.forEach((s) => (s.visible = levelGroups[s.userData.level].visible));
}
document.querySelectorAll("[data-show]").forEach((b) => (b.onclick = () => {
  b.classList.toggle("on"); levelGroups[b.dataset.show].visible = b.classList.contains("on");
  syncDoll();
}));
// orbit camera around the house: azimuth deg (0 = from the front/south, 90 = from the east), elevation deg, distance ft
function dollView(az, el, dist) {
  const a = az * Math.PI / 180, e = el * Math.PI / 180, t = new THREE.Vector3(47, 10, -27);
  orbit.target.copy(t);
  cam.position.set(t.x + dist * Math.cos(e) * Math.sin(a), t.y + dist * Math.sin(e), t.z + dist * Math.cos(e) * Math.cos(a));
  orbit.update();
}
function setMode(m) {
  mode = m;
  $("#mWalk").classList.toggle("on", m === "walk"); $("#mDoll").classList.toggle("on", m === "doll");
  $("#walkCtl").style.display = m === "walk" ? "contents" : "none";
  $("#dollCtl").style.display = m === "doll" ? "contents" : "none";
  stick.style.display = m === "walk" && isTouch ? "block" : "none";
  orbit.enabled = m === "doll";
  ceilings.forEach((c) => (c.visible = m === "walk"));     // dollhouse looks down into the rooms
  $("#help").textContent = m === "walk"
    ? (isTouch ? "Left thumb: move · Right thumb: look · Buttons above switch floors" : "WASD / arrows to move · drag to look")
    : "Drag to orbit · pinch to zoom · turn off Roof / floors above to look inside";
  if (m === "doll") { dollView(35, 28, 120); cam.rotation.order = "XYZ"; }
  else teleport(level, me.x, me.y, me.yaw * 180 / Math.PI);
  for (const g of Object.values(levelGroups)) g.visible = true;
  document.querySelectorAll("[data-show]").forEach((b) => b.classList.add("on"));
  syncDoll();
}
$("#mWalk").onclick = () => setMode("walk"); $("#mDoll").onclick = () => setMode("doll");
// ambient occlusion (GTAO) — on by default on desktop, toggle with the HQ button
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, cam));
const ao = new GTAOPass(scene, cam, innerWidth, innerHeight);
ao.updateGtaoMaterial({ radius: 1.2, thickness: 1.5, distanceExponent: 1.5, scale: 1.2, samples: 16 });
ao.updatePdMaterial({ radius: 8, rings: 2, samples: 16 });
const hideForAO = ao.overrideVisibility.bind(ao);      // glass and labels must not occlude
ao.overrideVisibility = function () {
  hideForAO();
  this.scene.traverse((o) => { if (o.material?.transparent) o.visible = false; });
};
composer.addPass(ao);
composer.addPass(new OutputPass());
let hq = !isTouch;
const hqBtn = $("#hq");
const setHQ = (on) => { hq = on; hqBtn.classList.toggle("on", on); };
hqBtn.onclick = () => setHQ(!hq); setHQ(hq);
addEventListener("resize", () => {
  cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight); composer.setSize(innerWidth, innerHeight);
});

// ---------- loop ----------
// optional deep link: #level/x/y/heading (e.g. #main/38/30/45), #doll, or #doll/azimuth/elevation/distance
const hash = location.hash.slice(1).split("/");
if (model.levels[hash[0]] && hash.length >= 3) teleport(hash[0], +hash[1], +hash[2], +(hash[3] ?? 0));
else teleport("main", ...SPAWN.main);
setMode(hash[0] === "doll" ? "doll" : "walk");
if (hash[0] === "doll" && hash.length >= 4) dollView(+hash[1], +hash[2], +hash[3]);
$("#loading").remove();
let last = performance.now();
renderer.setAnimationLoop((now) => {
  const dt = Math.min((now - last) / 1000, 0.1); last = now;
  if (mode === "walk") {
    let f = move.y, s = move.x;
    if (keys.has("KeyW") || keys.has("ArrowUp")) f += 1;
    if (keys.has("KeyS") || keys.has("ArrowDown")) f -= 1;
    if (keys.has("KeyD")) s += 1; if (keys.has("KeyA")) s -= 1;
    if (keys.has("ArrowLeft")) me.yaw -= dt * 1.8; if (keys.has("ArrowRight")) me.yaw += dt * 1.8;
    const m = Math.hypot(f, s); if (m > 1) { f /= m; s /= m; }
    const sy = Math.sin(me.yaw), cy = Math.cos(me.yaw);
    me.x += (sy * f + cy * s) * WALK_SPEED * dt; me.y += (cy * f - sy * s) * WALK_SPEED * dt;
    collide(); placeCamera();
  } else orbit.update();
  if (hq) composer.render(); else renderer.render(scene, cam);
});
