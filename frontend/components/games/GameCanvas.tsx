"use client";

import { Float, Html, OrbitControls, RoundedBox, Sparkles } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

import { WebGameCharacter, WebGameStep } from "@/lib/webgame-types";

type SceneKey = "cyber_office" | "inbox_room" | "account_lab" | "call_room" | string;

type GameObject = WebGameStep["options"][number] & {
  position: [number, number, number];
};

type Props = {
  character: WebGameCharacter | null;
  step: WebGameStep | null;
  sceneKey: SceneKey;
  disabled: boolean;
  onSelect: (value: string) => void;
};

const FALLBACK_POSITIONS: [number, number, number][] = [
  [-2.35, 0.55, 0],
  [0, 0.55, -0.35],
  [2.35, 0.55, 0],
  [-1.15, 0.55, -1.25],
  [1.15, 0.55, -1.25],
];

const SCENE_STYLE: Record<
  string,
  {
    background: string;
    floor: string;
    desk: string;
    accent: string;
    title: string;
  }
> = {
  cyber_office: {
    background: "#eef7ff",
    floor: "#dbeafe",
    desk: "#ffffff",
    accent: "#93c5fd",
    title: "Secure Desk",
  },
  inbox_room: {
    background: "#f5f3ff",
    floor: "#ede9fe",
    desk: "#ffffff",
    accent: "#a78bfa",
    title: "Inbox Room",
  },
  account_lab: {
    background: "#ecfdf5",
    floor: "#d1fae5",
    desk: "#ffffff",
    accent: "#34d399",
    title: "Account Lab",
  },
  call_room: {
    background: "#fff7ed",
    floor: "#ffedd5",
    desk: "#ffffff",
    accent: "#fb923c",
    title: "Social Trap",
  },
};

function CharacterModel({ character }: { character: WebGameCharacter | null }) {
  const group = useRef<THREE.Group>(null);
  const color = character?.color_primary || "#60a5fa";

  useFrame(({ clock }) => {
    if (!group.current) return;
    group.current.position.y = Math.sin(clock.elapsedTime * 1.6) * 0.035;
    group.current.rotation.y = Math.sin(clock.elapsedTime * 0.8) * 0.08;
  });

  return (
    <group ref={group} position={[0, 0, 1.75]}>
      <mesh position={[0, 1.45, 0]}>
        <sphereGeometry args={[0.34, 32, 32]} />
        <meshStandardMaterial color="#f4c7a1" roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.85, 0]}>
        <capsuleGeometry args={[0.34, 0.7, 8, 18]} />
        <meshStandardMaterial color={color} roughness={0.72} />
      </mesh>
      <mesh position={[-0.23, 1.55, 0.06]} rotation={[0.1, 0, 0.2]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      <mesh position={[0.23, 1.55, 0.06]} rotation={[0.1, 0, -0.2]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      <mesh position={[-0.52, 0.86, 0]} rotation={[0, 0, 0.45]}>
        <capsuleGeometry args={[0.09, 0.55, 6, 12]} />
        <meshStandardMaterial color={color} roughness={0.75} />
      </mesh>
      <mesh position={[0.52, 0.86, 0]} rotation={[0, 0, -0.45]}>
        <capsuleGeometry args={[0.09, 0.55, 6, 12]} />
        <meshStandardMaterial color={color} roughness={0.75} />
      </mesh>
      <Html position={[0, 2.05, 0]} center>
        <div className="game3d-nameplate">{character?.name || "Cyber Agent"}</div>
      </Html>
    </group>
  );
}

function ThreatObject({
  item,
  disabled,
  onSelect,
}: {
  item: GameObject;
  disabled: boolean;
  onSelect: (value: string) => void;
}) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.rotation.y = Math.sin(clock.elapsedTime + item.position[0]) * 0.05;
  });

  const height = item.kind === "safe" ? 0.72 : item.kind === "danger" ? 0.88 : 0.78;

  return (
    <Float speed={1.2} rotationIntensity={0.08} floatIntensity={0.12}>
      <group position={item.position}>
        <RoundedBox
          ref={ref}
          args={[1.45, height, 0.16]}
          radius={0.08}
          smoothness={5}
          onClick={() => !disabled && onSelect(item.value)}
        >
          <meshStandardMaterial color={item.color} roughness={0.62} />
        </RoundedBox>
        <Html position={[0, 0.02, 0.12]} center>
          <button
            className={`game3d-object-label ${item.kind}`}
            disabled={disabled}
            onClick={() => !disabled && onSelect(item.value)}
          >
            {item.label}
          </button>
        </Html>
      </group>
    </Float>
  );
}

function SceneDecor({ sceneKey }: { sceneKey: SceneKey }) {
  if (sceneKey === "inbox_room") {
    return (
      <>
        <RoundedBox args={[0.9, 1.1, 0.12]} radius={0.05} position={[-3.1, 0.85, -1.4]}>
          <meshStandardMaterial color="#ddd6fe" />
        </RoundedBox>
        <RoundedBox args={[0.9, 1.1, 0.12]} radius={0.05} position={[3.1, 0.85, -1.4]}>
          <meshStandardMaterial color="#c4b5fd" />
        </RoundedBox>
      </>
    );
  }
  if (sceneKey === "account_lab") {
    return (
      <>
        <mesh position={[-3.05, 0.72, -1.2]}>
          <torusGeometry args={[0.34, 0.08, 14, 28]} />
          <meshStandardMaterial color="#34d399" />
        </mesh>
        <mesh position={[3.05, 0.72, -1.2]}>
          <boxGeometry args={[0.7, 0.7, 0.12]} />
          <meshStandardMaterial color="#86efac" />
        </mesh>
      </>
    );
  }
  if (sceneKey === "call_room") {
    return (
      <>
        <mesh position={[-3.0, 0.8, -1.25]} rotation={[0, 0, -0.15]}>
          <capsuleGeometry args={[0.18, 0.7, 8, 18]} />
          <meshStandardMaterial color="#fb923c" />
        </mesh>
        <mesh position={[3.0, 0.8, -1.25]} rotation={[0, 0, 0.15]}>
          <capsuleGeometry args={[0.18, 0.7, 8, 18]} />
          <meshStandardMaterial color="#fdba74" />
        </mesh>
      </>
    );
  }
  return null;
}

function CyberScene({ character, step, sceneKey, disabled, onSelect }: Props) {
  const style = SCENE_STYLE[sceneKey] || SCENE_STYLE.cyber_office;
  const objects: GameObject[] = useMemo(
    () =>
      (step?.options || []).map((item, index) => ({
        ...item,
        position: item.position || FALLBACK_POSITIONS[index] || [0, 0.55, 0],
      })),
    [step],
  );

  return (
    <>
      <color attach="background" args={[style.background]} />
      <ambientLight intensity={0.78} />
      <directionalLight position={[3, 5, 4]} intensity={1.12} />
      <Sparkles count={24} scale={[6, 2, 4]} size={1.8} speed={0.2} color={style.accent} />

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <planeGeometry args={[8, 6]} />
        <meshStandardMaterial color={style.floor} roughness={0.9} />
      </mesh>

      <RoundedBox args={[6.2, 0.18, 1.25]} radius={0.08} position={[0, 0.2, 0]}>
        <meshStandardMaterial color={style.desk} roughness={0.8} />
      </RoundedBox>

      <SceneDecor sceneKey={sceneKey} />
      <CharacterModel character={character} />

      {objects.map((item) => (
        <ThreatObject
          key={item.value}
          item={item}
          disabled={disabled || !step}
          onSelect={onSelect}
        />
      ))}

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        minPolarAngle={Math.PI / 3.5}
        maxPolarAngle={Math.PI / 2.25}
      />
    </>
  );
}

export default function GameCanvas(props: Props) {
  return (
    <Canvas
      dpr={[1, 1.5]}
      camera={{ position: [0, 3.35, 5.6], fov: 45 }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <CyberScene {...props} />
    </Canvas>
  );
}
