
//Constant buffer four our data.
cbuffer defaultBuffer  
{
    float4 ambientColor;
    float4 diffuseColor;
    float4 specularColor;
    float3 lightPos;

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

struct VS_OUTPUT{
    float4 pos: POSITION;
    float4 color: COLOR;
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

	const float attenuation = 0.005f;
    //Transform our world-space vertex into screen space.
    output.pos = mul(input.pos, WVPMatrix);

    float4 worldNormal = mul(input.normal, worldMatrix);
    float4 worldPos = mul(input.pos, worldMatrix);
    worldPos = worldPos/worldPos.w;

	float3 toLight = lightPos.xyz - worldPos.xyz;
    float3 directionToLight = normalize(toLight);
	float lightDist = length(toLight);
	float fAtten = 1.0 / dot(attenuation, float4(1, lightDist, lightDist * lightDist, 0));
    float diffuseIntensity = saturate( dot(worldNormal.xyz, directionToLight) * fAtten );
    float4 diffuse = diffuseColor * diffuseIntensity;

    float3 reflectionVector = normalize( reflect(-directionToLight, worldNormal.xyz) );
    float3 directionToCamera = normalize( cameraPos - worldPos.xyz );
    float4 specular = specularColor * pow(saturate(dot(reflectionVector, directionToCamera)), 20);

    output.color = specular + diffuse + ambientColor;
	//output.color = diffuse;
    output.color.a = 1.0;
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
