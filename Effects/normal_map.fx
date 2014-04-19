
//Constant buffer four our data.
cbuffer defaultBuffer  
{
    float4 vLightDirection;
    float3 vEye;

    float4 diffuseColor;
    float4 specularColor;
    float4 ambientColor;

    //inv World matrix
    float4x4 worldMatrix;
    //Combined world-, view- and projection-matrix.
    float4x4 worldViewProjection;
}

// //Pre-object buffer
// cbuffer perObjectBuffer
// {
//     //Combined view and projection matrix
//     float4x4 viewProjection;
// }

Texture2D ColorMap;
SamplerState ColorMapSampler
{
    Filter = MIN_MAG_MIP_LINEAR;
    AddressU = CLAMP;
    AddressV = CLAMP;
};
 
Texture2D NormalMap;
SamplerState NormalMapSampler
{
    Filter = MIN_MAG_MIP_LINEAR;
    AddressU = CLAMP;
    AddressV = CLAMP;
};

struct VS_INPUT {
    float4 pos: POSITION;
    float2 tex: TEXCOORD;
    float4 normal: NORMAL;
    float4 tangent: TANGENT;
};

//Our input vertex for the vertex shader.
struct PS_INPUT {
    float4 pos : SV_POSITION; //World-space position.
    float2 tex: TEXCOORD0;
    float4 light: TEXCOORD1;
    float4 view: TEXCOORD2;
};

// //Data from vertex shader into pixel shader.
// struct PS_INPUT {
//     float4 pos : SV_POSITION; //Final "2D-position".
//     float4 color : COLOR; 
// };

//Vertex shader.
PS_INPUT VSSimple(VS_INPUT input)
{
    PS_INPUT output;

    //Transform our world-space vertex into screen space.
    output.pos = mul(input.pos, worldViewProjection);

    float4x4 worldToTangentSpace;
    worldToTangentSpace[0] = mul(input.tangent, worldMatrix);
    worldToTangentSpace[1] = mul(cross(input.tangent, input.normal), worldMatrix);
    worldToTangentSpace[2] = mul(input.normal, worldMatrix);
    worldToTangentSpace[3] = float4(0,0,0,1);
    output.tex = input.tex;
    float4 posWorld = mul(input.pos, worldMatrix);
    output.light = mul(worldToTangentSpace, vLightDirection);
    output.view = mul(worldToTangentSpace, vEye - posWorld);
    //Copy vertex color through for the pixel shader.
    //output.color = input.color;
    return output;    
}

//Pixels shader just returns the vertex color. SV_Target# semantic
//means the color will go to the render target at index 0.
float4 PSSimple(PS_INPUT input) : SV_Target
{
    float4 color = ColorMap.Sample(ColorMapSampler, input.tex);
    float3 normal = (2 * (NormalMap.Sample(NormalMapSampler, input.tex))) - 1.0;
    float3 lightDir = normalize(input.light);
    float3 viewDir = normalize(input.view);
    float diffuse = saturate(dot(normal, lightDir));
    float3 reflection = normalize(2*diffuse*normal - lightDir);
    float specular = min(pow(saturate(dot(reflection, viewDir)), 3), color.w);
    return 0.2 * color + color*diffuse + specular;
}

//Disable culling.
RasterizerState RSNoCull { 
    CullMode = None; 
};

technique11 Render {
    pass {       
        SetVertexShader(CompileShader(vs_4_0, VSSimple())); 
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_4_0, PSSimple()));    
    
        SetRasterizerState(RSNoCull);
    }
}
