
//Constant buffer four our data.
cbuffer defaultBuffer  
{

    float4 ambientColor;
    float4 diffuseColor;
    float4 specularColor;
    float3 lightPos;
    float3 lightDir;

    //camera position
    float3 cameraPos;
    //inv World matrix
    float4x4 worldMatrix;
    //Combined world-, view- and projection-matrix.
    float4x4 WVPMatrix;
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

//Data from vertex shader into pixel shader.
struct PS_INPUT {
    float4 pos: SV_POSITION;
    float4 worldPos: POSITION;
    float4 worldNormal: COLOR;
};

//Vertex shader.
PS_INPUT VSSimple(VS_INPUT input)
{
    PS_INPUT output;

    output.pos = mul(input.pos, WVPMatrix);
    output.worldNormal = normalize( mul(input.normal, worldMatrix) );
    float4 worldPos = mul(input.pos, worldMatrix);
    output.worldPos = worldPos/worldPos.w;
    return output;
}

//Pixels shader just returns the vertex color. SV_Target# semantic
//means the color will go to the render target at index 0.
float4 PSSimple(PS_INPUT input) : SV_Target
{
    //float3 directionToLight = normalize(lightPos.xyz - input.worldPos.xyz);
    float3 directionToLight = normalize(float3(1, 0, 0));
    float diffuseIntensity =  dot(directionToLight, input.worldNormal.xyz);
    float4 diffuse = diffuseColor * diffuseIntensity;

    float3 reflectionVector = normalize( reflect(-directionToLight, input.worldNormal.xyz) );
    float3 directionToCamera = normalize( cameraPos - input.worldPos.xyz );
    float4 specular = specularColor * pow(saturate(dot(reflectionVector, directionToCamera)), 20);

    float4 color = specular + diffuse + ambientColor;
    color.a = 1.0;
    return color;
}

//Disable culling.
RasterizerState RSNoCull { 
    CullMode = None; 
};

technique11 Render {
    pass {       
        SetVertexShader(CompileShader(vs_4_0, VSSimple()));  // 
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_4_0, PSSimple()));    
    
        SetRasterizerState(RSNoCull);
    }
}
