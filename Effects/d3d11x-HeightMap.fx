
#include "Shared.fx"

cbuffer HeightMapBuffer
{
    int visualizeNormals = 0;
}

SamplerState mirrorSampler {
    Filter = ANISOTROPIC; // Or MIN_MAG_MIP_LINEAR.
    AddressU = MIRROR; 
    AddressV = MIRROR;
    MaxAnisotropy = 8;
};

struct VS_INPUT {
    float4 position : POSITION;
    float3 normal : NORMAL;
    float2 tex : TEXTURE;
};

struct VS_OUTPUT {
    float4 position : SV_POSITION;   
    float4 color : COLOR;
    float2 tex : TEXTURE;
};

VS_OUTPUT RenderMapVS(VS_INPUT input)
{
    VS_OUTPUT output;
    output.position = mul(input.position, worldMatrix);

    const float3 normal = mul(input.normal, (float3x3)worldMatrix);
    if (visualizeNormals) {
        //Visualize normal as a color.
        output.color.rgb = (-normal) * 0.5 + 0.5;
        output.color.a = 1;
    }
    else {
        output.color = ComputeLight(output.position.xyz, normal);
    }
    output.position = mul(output.position, viewProjection);
    output.tex = input.tex;
    
    return output;    
}

float4 RenderMapPS(VS_OUTPUT input) : SV_Target
{ 
    if (visualizeNormals) {
        return input.color;
    }
    else {
        return defaultTexture.Sample(mirrorSampler, input.tex) * input.color;
    }
}

RasterizerState RSNormal { 
    CullMode = Front; 
    MultisampleEnable = True;
    //FillMode = WireFrame;
};

technique11 RenderMap {
    pass {       
        SetVertexShader(CompileShader(vs_4_0, RenderMapVS())); 
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_4_0, RenderMapPS()));    
    
        SetRasterizerState(RSNormal);
    }
}
