
//Constant buffer four our data.
cbuffer defaultBuffer  
{

    //float4 ambientColor;
    //float4 diffuseColor;
    //float4 specularColor;

    //camera position
    float3 cameraPos;
    //inv World matrix
    float4x4 worldMatrix;
    //Combined world-, view- and projection-matrix.
    float4x4 WVPMatrix;

	float3 lightDir;
	float4 lightColor;
}

// //Pre-object buffer
// cbuffer perObjectBuffer
// {
//     //Combined view and projection matrix
//     float4x4 viewProjection;
// }

struct VertexInput
{
    float4  Position : POSITION;
    float4  Normal : NORMAL;
};


struct VertexOutput
{
    float4  Position : SV_POSITION;
    float3  Normal : TEXCOORD1;
    float3  View     : TEXCOORD2;        
};


VertexOutput VertexMain(VertexInput input)
{
    VertexOutput output = (VertexOutput)0;
    
     output.Position = mul(input.Position, WVPMatrix);
     output.Normal = mul(input.Normal, worldMatrix);
     output.View  = cameraPos - mul(input.Position,  worldMatrix);
     
     return output;
}

float4 PixelMain(VertexOutput input) : SV_Target
{
    float diffsum;
    float specularsum;
    float4 color;
    float sunshinepower;
    float4 amibent = float4(0.5f, 0.5f, 0.5f, 1.0f);
    sunshinepower = 20.0f;
    
    diffsum = specularsum = 0;
    
    //Âþ·´Éä
    float3 l = normalize(lightDir);
    diffsum = saturate(dot(l, input.Normal));
    
    //¾µÃæ·´Éä
    float3 L = -lightDir;
    float3 R = normalize(reflect(L, input.Normal));
    float3 V = normalize(input.View);
    
    specularsum = pow(saturate(dot(R, V)), sunshinepower);
    
    color = specularsum + diffsum * lightColor + amibent;

    
    return color;
}


//Disable culling.
RasterizerState RSNoCull { 
    CullMode = None; 
};

technique11 Render {
    pass {       
        SetVertexShader(CompileShader(vs_4_0, VertexMain()));  // 
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_4_0, PixelMain()));    
    
        SetRasterizerState(RSNoCull);
    }
}
