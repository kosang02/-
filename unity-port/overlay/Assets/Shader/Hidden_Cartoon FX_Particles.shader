// Independent unlit particle replacement for recovered dummy shaders.
Shader "Hidden/Cartoon FX/Particles" {
 Properties { _MainTex ("Particle",2D)="white" {} _TintColor ("Tint",Color)=(.5,.5,.5,.5) _BaseColor ("Base",Color)=(.5,.5,.5,.5) _InvFade ("Fade",Range(.01,3))=1 }
 SubShader {
  Tags { "Queue"="Transparent" "RenderType"="Transparent" "IgnoreProjector"="True" }
  Blend SrcAlpha OneMinusSrcAlpha
  Cull Off Lighting Off ZWrite Off
  Pass {
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #include "UnityCG.cginc"
   sampler2D _MainTex; float4 _MainTex_ST; fixed4 _TintColor;
   struct input { float4 vertex:POSITION; fixed4 color:COLOR; float2 uv:TEXCOORD0; };
   struct output { float4 vertex:SV_POSITION; fixed4 color:COLOR; float2 uv:TEXCOORD0; };
   output vert(input v) { output o; o.vertex=UnityObjectToClipPos(v.vertex);o.color=v.color;o.uv=TRANSFORM_TEX(v.uv,_MainTex);return o; }
   fixed4 frag(output i):SV_Target { fixed4 tex=tex2D(_MainTex,i.uv); return 2*i.color*_TintColor*tex; }
   ENDCG
  }
 }
}
