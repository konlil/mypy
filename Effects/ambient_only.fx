
//Constant buffer four our data.
cbuffer defaultBuffer  
{
    //Combined world-, view- and projection-matrix.
    float4x4 worldViewProjection;
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
    //return input.color;
    return float4(1.0f, 0.3f, 0.7f, 1.0f);
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
