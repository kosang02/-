// Independent compatibility shader retaining recovered material property names.
Shader "FX/Water" {
 Properties {
  _WaveScale ("Wave scale", Range(.02,.15)) = .063
  _ReflDistort ("Reflection distortion", Range(0,1.5)) = .44
  _RefrDistort ("Refraction distortion", Range(0,1.5)) = .4
  _RefrColor ("Water tint", Color) = (.34,.85,.92,1)
  _Fresnel ("Fresnel", 2D) = "gray" {}
  _BumpMap ("Normal map", 2D) = "bump" {}
  WaveSpeed ("Wave speed", Vector) = (19,9,-16,-7)
  _ReflectiveColor ("Reflective color", 2D) = "gray" {}
  _HorizonColor ("Horizon", Color) = (.172,.463,.435,1)
  _ReflectionTex ("Reflection", 2D) = "black" {}
  _RefractionTex ("Refraction", 2D) = "gray" {}
 }
 SubShader {
  Tags { "RenderType"="Opaque" "Queue"="Geometry+1" "WaterMode"="Refractive" }
  Pass {
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 2.0
   #pragma multi_compile WATER_SIMPLE WATER_REFLECTIVE WATER_REFRACTIVE
   #include "UnityCG.cginc"
   sampler2D _BumpMap,_ReflectionTex,_RefractionTex,_ReflectiveColor;
   float _WaveScale,_ReflDistort,_RefrDistort;
   float4 _HorizonColor,_RefrColor,WaveSpeed;
   struct v2f { float4 pos:SV_POSITION; float4 screen:TEXCOORD0; float4 waves:TEXCOORD1; float3 view:TEXCOORD2; };
   v2f vert(appdata_base v) {
    v2f o; o.pos=UnityObjectToClipPos(v.vertex); o.screen=ComputeScreenPos(o.pos);
    float3 world=mul(unity_ObjectToWorld,v.vertex).xyz;
    o.waves=float4(world.xz,world.xz)*_WaveScale+WaveSpeed*_Time.y*.001;
    o.view=_WorldSpaceCameraPos-world; return o;
   }
   fixed4 frag(v2f i):SV_Target {
    float3 n1=UnpackNormal(tex2D(_BumpMap,i.waves.xy));
    float3 n2=UnpackNormal(tex2D(_BumpMap,i.waves.zw));
    float3 n=normalize(float3(n1.x+n2.x,2,n1.y+n2.y));
    float fresnel=pow(1-saturate(dot(normalize(i.view),n)),3);
    float2 uv=i.screen.xy/i.screen.w;
    float3 color=lerp(_RefrColor.rgb*.55,_HorizonColor.rgb,fresnel);
    #if defined(WATER_REFRACTIVE)
     float3 refr=tex2D(_RefractionTex,uv+n.xz*_RefrDistort*.03).rgb;
     color=lerp(color,refr*_RefrColor.rgb,.65);
    #endif
    #if defined(WATER_REFLECTIVE) || defined(WATER_REFRACTIVE)
     float3 refl=tex2D(_ReflectionTex,uv+n.xz*_ReflDistort*.025).rgb;
     color=lerp(color,refl,.16+fresnel*.65);
    #endif
    color+=pow(saturate(n.y),24)*.025;
    return fixed4(color,1);
   }
   ENDCG
  }
 }
 Fallback "Diffuse"
}
