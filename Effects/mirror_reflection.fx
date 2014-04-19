
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

struct VS_INPUT {
    float4 pos: POSITION;
    float4 normal: NORMAL;
};

//Our input vertex for the vertex shader.
struct PS_INPUT {
    float4 pos : SV_POSITION; //World-space position.
    float4 light_dir: TEXCOORD0;
    float4 normal: TEXCOORD1;
    float4 view : TEXCOORD2;
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
    output.light_dir = normalize(vLightDirection);
    output.normal = normalize(mul(input.normal, worldMatrix));
    float4 posWorld = mul(input.pos, worldMatrix);
    output.view = float4(vEye, 1.0) - posWorld;
    //Copy vertex color through for the pixel shader.
    //output.color = input.color;
    return output;    
}

//Pixels shader just returns the vertex color. SV_Target# semantic
//means the color will go to the render target at index 0.
float4 PSSimple(PS_INPUT input) : SV_Target
{
    float3 normal = normalize(input.normal.xyz);
    float3 lightDir = normalize(input.light_dir.xyz);
    float3 viewDir = normalize(input.view.xyz);
    float diff = saturate(dot(normal, lightDir));
    // R = 2*(N.L) * N - L
    float3 rflct = normalize(2*diff*normal - lightDir);
    float specular = pow(saturate(dot(rflct, viewDir)), 1);

    // I = A + Dcolor * Dintensit * N.L + Scolor * Sintensity * (R.V)n
    return ambientColor + diffuseColor * diff + specularColor * specular;
    // return specularColor * specular;
    // return float4(lightDir, 1.0);
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
