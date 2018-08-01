//Maya ASCII 2015 scene
//Name: meshComponentInfoSample01.ma
//Last modified: Sat, Jun 02, 2018 10:19:11 AM
//Codeset: 1252
requires maya "2015";
requires -nodeType "meshComponentInfo" "meshComponentInfo.py" "0.0.1";
currentUnit -l centimeter -a degree -t film;

createNode transform -n "meshExample";
	setAttr ".t" -type "double3" -3.6472148266145905 3.8819612588193975 2.9679754715286357 ;
	setAttr ".r" -type "double3" 4.3061000353541861 -29.8361891558603 -40.283363646495928 ;
createNode mesh -n "meshExampleShape" -p "meshExample";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "drivenNode";
createNode locator -n "drivenNodeShape" -p "drivenNode";
	setAttr -k off ".v";

createNode polyCube -n "meshExampleSource";
	setAttr ".sw" 5;
	setAttr ".sh" 3;
	setAttr ".sd" 4;
	setAttr ".cuv" 4;

createNode meshComponentInfo -n "drivenNode_ComponentConstraint1";

createNode script -n "uiConfigurationScriptNode";
	addAttr -ci true -sn "config" -ln "config" -dt "string";
	setAttr -av ".b";
	setAttr ".st" 3;
	setAttr ".ire" 1;

select -ne :time1;
	setAttr ".o" 1;

connectAttr "meshExampleSource.out" "meshExampleShape.i";
connectAttr "drivenNode_ComponentConstraint1.out" "drivenNode.t";
connectAttr "meshExampleShape.w" "drivenNode_ComponentConstraint1.in";
connectAttr "uiConfigurationScriptNode.config" "uiConfigurationScriptNode.b";

// End of meshComponentInfoSample01.ma
