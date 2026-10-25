import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";

const EYE = 5.5, RADIUS = 1.1, WALK_SPEED = 4.5;       // feet, feet/sec
const SPAWN = { basement: [40, 18, 90], main: [21, 5, 0], upper: [30, 16, 0] }; // x, y, heading deg (0 = north)
const COLORS = { floor: 0xb8a88a, wallExt: 0xe7e1d3, wallInt: 0xf4f1ea, doorExt: 0x6b4f3a,
  garageDoor: 0xc3c6ca, slabOut: 0x9a9a96, stair: 0x8c6f52 };

const isTouch = matchMedia("(pointer: coarse)").matches;
const $ = (s) => document.querySelector(s);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xbfd6e6);
scene.add(new THREE.HemisphereLight(0xffffff, 0x6b6b66, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(40, 80, 30);
scene.add(sun);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600),
  new THREE.MeshStandardMaterial({ color: 0x7c9a62, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.position.set(47, -0.02, -31);
scene.add(ground);

const cam = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.1, 800);
const orbit = new OrbitControls(cam, renderer.domElement);
orbit.target.set(47, 5, -31);
orbit.enableDamping = true;

const mats = {};
function mat(name) {
  if (mats[name]) return mats[name];
  let m;
  if (name === "glass") m = new THREE.MeshStandardMaterial({ color: 0x9ad0e6, transparent: true, opacity: 0.35, roughness: 0.1 });
  else if (name.startsWith("fix:")) m = new THREE.MeshStandardMaterial({ color: name.slice(4), roughness: 0.8 });
  else m = new THREE.MeshStandardMaterial({ color: COLORS[name] ?? 0xcccccc, roughness: 0.9 });
  return (mats[name] = m);
}

const model = await (await fetch("./model.json")).json();
const levelGroups = {}, colliders = [];
for (const [lvl, L] of Object.entries(model.levels)) {
  const g = new THREE.Group();
  for (const [x, y, z, w, d, h, m, c] of L.boxes) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(m));
    mesh.position.set(x + w / 2, z + h / 2, -(y + d / 2));
    g.add(mesh);
    if (c) colliders.push({ x0: x, x1: x + w, y0: y, y1: y + d, z0: z, z1: z + h });
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
document.querySelectorAll("[data-show]").forEach((b) => (b.onclick = () => {
  b.classList.toggle("on"); levelGroups[b.dataset.show].visible = b.classList.contains("on");
  labels.children.forEach((s) => (s.visible = levelGroups[s.userData.level].visible));
}));
function setMode(m) {
  mode = m;
  $("#mWalk").classList.toggle("on", m === "walk"); $("#mDoll").classList.toggle("on", m === "doll");
  $("#walkCtl").style.display = m === "walk" ? "contents" : "none";
  $("#dollCtl").style.display = m === "doll" ? "contents" : "none";
  stick.style.display = m === "walk" && isTouch ? "block" : "none";
  labels.visible = m === "doll"; orbit.enabled = m === "doll";
  ground.material.transparent = m === "doll"; ground.material.opacity = m === "doll" ? 0.3 : 1;
  ground.material.depthWrite = m !== "doll"; ground.material.needsUpdate = true;
  $("#help").textContent = m === "walk"
    ? (isTouch ? "Left thumb: move · Right thumb: look · Buttons above switch floors" : "WASD / arrows to move · drag to look")
    : "Drag to orbit · pinch to zoom · toggle floors above";
  if (m === "doll") { cam.position.set(47, 90, 30); orbit.target.set(47, 5, -25); cam.rotation.order = "XYZ"; orbit.update(); }
  else teleport(level, me.x, me.y, me.yaw * 180 / Math.PI);
  for (const g of Object.values(levelGroups)) g.visible = true;
  document.querySelectorAll("[data-show]").forEach((b) => b.classList.add("on"));
}
$("#mWalk").onclick = () => setMode("walk"); $("#mDoll").onclick = () => setMode("doll");
addEventListener("resize", () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });

// ---------- loop ----------
teleport("main", ...SPAWN.main); setMode("walk");
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
  renderer.render(scene, cam);
});
