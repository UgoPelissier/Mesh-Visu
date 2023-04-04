// Gmsh project created on Mon Jan 09 15:15:05 2023
SetFactory("OpenCASCADE");

R = DefineNumber[ 1.4 , Min 0.1, Max 2, Step 0.01,
  Name "Parameters/Box dimension" ];
Rt = DefineNumber[ R*1.25, Min 0.1, Max 2, Step 0.01,
  Name "Parameters/Sphere radius" ];

Box(1) = {0,0,0, 1,1,1};

Sphere(2) = {1,0.5,0.5,0.5};

BooleanUnion(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
