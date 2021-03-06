
//Constant buffer four our data.
cbuffer defaultBuffer  
{
    //World matrix
    float4x4 worldMatrix;
    //Combined world-, view- and projection-matrix.
    float4x4 worldViewProjection;
}

//Pre-object buffer
cbuffer perObjectBuffer
{
    //Combined view and projection matrix
    float4x4 viewProjection;

    //Lightning info.
    float4 lightAmbient = float4(0.2, 0.2, 0.2, 0);
    float3 lightPositions[MAX_LIGHT_COUNT];
    float4 lightColors[MAX_LIGHT_COUNT]; //Values can be over 1.0, not normalized.
    uint lightsActive = 0;
}

//Our input vertex for the vertex shader.
struct VS_INPUT {
    float4 pos : POSITION; //World-space position.
    float4 color : COLOR; //Vertex color.
};

//Data from vertex shader into pixel shader.
struct PS_INPUT {
    float4 pos : SV_POSITION; //Final "2D-position".
    float4 color : COLOR; 
};

//Vertex shader.
PS_INPUT VSSimple(VS_INPUT input)
{
    PS_INPUT output;
    //Transform our world-space vertex into screen space.
    output.pos = mul(input.pos, worldViewProjection);
    //Copy vertex color through for the pixel shader.
    output.color = input.color;
    return output;    
}

//Pixels shader just returns the vertex color. SV_Target# semantic
//means the color will go to the render target at index 0.
float4 PSSimple(PS_INPUT input) : SV_Target
{ 
    return input.color;
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
