requires maya "2015";

requires -nodeType "report" -nodeType "reportLocator" "report.py" "0.0.1";
currentUnit -l centimeter -a degree -t film;

createNode transform -n "reportHandle";
	setAttr ".t" -type "double3" -13.695 9.007 6.94 ;
	setAttr ".r" -type "double3" -72.170078079556916 -45.174197124920163 -69.051673372424702 ;
	setAttr ".s" -type "double3" 1 1 1 ;
createNode reportLocator -n "reportLocator1" -p "reportHandle";
	setAttr -k off ".v";
createNode report -n "report1";
	addAttr -ci true -sn "nts" -ln "notes" -dt "string";
	setAttr ".itp" 1;
	setAttr ".num" 16.541;
	setAttr ".nts" -type "string" "Scene Report:\nCharacter was saved on february 2018\n**********************************************************************\n\nThe next version of the rig needs to be optimized.\n\n\nPoint  position is:\n\n";

createNode script -n "uiConfigurationScriptNode";
	addAttr -ci true -sn "config" -ln "config" -dt "string";
	setAttr -av ".b";
	setAttr ".st" 3;
	setAttr ".ire" 1;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 0;

select -ne :defaultRenderingList1;
connectAttr "report1.out" "reportLocator1.txt";
connectAttr "report1.nts" "report1.inLbl";
connectAttr "reportHandle.t" "report1.t";
connectAttr "reportHandle.r" "report1.r";
connectAttr "uiConfigurationScriptNode.config" "uiConfigurationScriptNode.b";

// End of reportSample01.ma
