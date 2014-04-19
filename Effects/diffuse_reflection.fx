
//Constant buffer four our data.
cbuffer defaultBuffer  
{
    float4 vLightDirection;
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
    //float4 color : COLOR; //Vertex color.
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
    //Copy vertex color through for the pixel shader.
    //output.color = input.color;
    return output;    
}

//Pixels shader just returns the vertex color. SV_Target# semantic
//means the color will go to the render target at index 0.
float4 PSSimple(PS_INPUT input) : SV_Target
{
    float Ai = 0.8f;
    float4 Ac = float4(0.075, 0.075, 0.2, 1.0);
    float Di = 1.0f;
    float4 Dc = float4(1.0, 1.0, 1.0, 1.0); 
    return Ai*Ac + Di*Dc*saturate(dot(input.light_dir, input.normal));
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
