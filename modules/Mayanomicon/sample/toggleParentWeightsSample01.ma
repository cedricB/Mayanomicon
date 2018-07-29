//Maya ASCII 2015 scene
//Name: toggleParentWeightsSample01.ma
//Last modified: Fri, Jul 27, 2018 04:47:02 AM
//Codeset: 1252
requires maya "2015";
currentUnit -l centimeter -a degree -t film;

createNode transform -n "drivenElement";
createNode mesh -n "drivenElementShape" -p "drivenElement";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;

	setAttr -s 8 ".vt[0:7]"  -0.5 -0.5 0.5 0.5 -0.5 0.5 -0.5 0.5 0.5 0.5 0.5 0.5
		 -0.5 0.5 -0.5 0.5 0.5 -0.5 -0.5 -0.5 -0.5 0.5 -0.5 -0.5;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces" 
		f 4 0 5 -2 -5
		mu 0 4 0 1 3 2
		f 4 1 7 -3 -7
		mu 0 4 2 3 5 4
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -12 -10 -8 -6
		mu 0 4 1 10 11 3
		f 4 10 4 6 8
		mu 0 4 12 0 2 13;

createNode parentConstraint -n "drivenElement_parentConstraint1" -p "drivenElement";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "headSpaceW0" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w1" -ln "handSpaceW1" -dv 1 -min 0 -at "double";
	addAttr -dcb 0 -ci true -k true -sn "w2" -ln "rootSpaceW2" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 3 ".tg";
	setAttr ".lr" -type "double3" 15.238297257451837 -11.286254549423584 1.7268931989524881 ;
	setAttr ".rst" -type "double3" -0.41558946101982264 0.0556672835645197 0.039041451569994237 ;
	setAttr ".rsrr" -type "double3" 15.238297257451837 -11.286254549423584 1.7268931989524881 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
	setAttr -k on ".w2";
createNode transform -n "headSpace";
	setAttr ".t" -type "double3" -3.2869631316553534 1.5772397009865315 -0.72901157691676843 ;
	setAttr ".r" -type "double3" -4.0826640177956914 -18.674150760338204 24.420686614615928 ;
createNode locator -n "headSpaceShape" -p "headSpace";
	setAttr -k off ".v";
createNode transform -n "handSpace";
	setAttr ".t" -type "double3" 2.3725703141149621 1.7256857904910134 -2.088145141022931 ;
	setAttr ".r" -type "double3" 23.223723943022836 -5.1734044098622816 -8.114163249521317 ;
createNode locator -n "handSpaceShape" -p "handSpace";
	setAttr -k off ".v";
createNode transform -n "rootSpace";
	setAttr ".t" -type "double3" -0.33237556551907677 -3.1359236407839859 2.9342810726496822 ;
	setAttr ".r" -type "double3" 23.223723943022836 -5.1734044098622816 -8.114163249521317 ;
createNode locator -n "rootSpaceShape" -p "rootSpace";
	setAttr -k off ".v";

createNode script -n "uiConfigurationScriptNode";
	addAttr -ci true -sn "config" -ln "config" -dt "string";
	setAttr -av ".b";
	setAttr ".st" 3;
	setAttr ".ire" 1;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;

connectAttr "drivenElement_parentConstraint1.ctx" "drivenElement.tx";
connectAttr "drivenElement_parentConstraint1.cty" "drivenElement.ty";
connectAttr "drivenElement_parentConstraint1.ctz" "drivenElement.tz";
connectAttr "drivenElement_parentConstraint1.crx" "drivenElement.rx";
connectAttr "drivenElement_parentConstraint1.cry" "drivenElement.ry";
connectAttr "drivenElement_parentConstraint1.crz" "drivenElement.rz";
connectAttr "drivenElement.ro" "drivenElement_parentConstraint1.cro";
connectAttr "drivenElement.pim" "drivenElement_parentConstraint1.cpim";
connectAttr "drivenElement.rp" "drivenElement_parentConstraint1.crp";
connectAttr "drivenElement.rpt" "drivenElement_parentConstraint1.crt";
connectAttr "headSpace.t" "drivenElement_parentConstraint1.tg[0].tt";
connectAttr "headSpace.rp" "drivenElement_parentConstraint1.tg[0].trp";
connectAttr "headSpace.rpt" "drivenElement_parentConstraint1.tg[0].trt";
connectAttr "headSpace.r" "drivenElement_parentConstraint1.tg[0].tr";
connectAttr "headSpace.ro" "drivenElement_parentConstraint1.tg[0].tro";
connectAttr "headSpace.s" "drivenElement_parentConstraint1.tg[0].ts";
connectAttr "headSpace.pm" "drivenElement_parentConstraint1.tg[0].tpm";
connectAttr "drivenElement_parentConstraint1.w0" "drivenElement_parentConstraint1.tg[0].tw"
		;
connectAttr "handSpace.t" "drivenElement_parentConstraint1.tg[1].tt";
connectAttr "handSpace.rp" "drivenElement_parentConstraint1.tg[1].trp";
connectAttr "handSpace.rpt" "drivenElement_parentConstraint1.tg[1].trt";
connectAttr "handSpace.r" "drivenElement_parentConstraint1.tg[1].tr";
connectAttr "handSpace.ro" "drivenElement_parentConstraint1.tg[1].tro";
connectAttr "handSpace.s" "drivenElement_parentConstraint1.tg[1].ts";
connectAttr "handSpace.pm" "drivenElement_parentConstraint1.tg[1].tpm";
connectAttr "drivenElement_parentConstraint1.w1" "drivenElement_parentConstraint1.tg[1].tw"
		;
connectAttr "rootSpace.t" "drivenElement_parentConstraint1.tg[2].tt";
connectAttr "rootSpace.rp" "drivenElement_parentConstraint1.tg[2].trp";
connectAttr "rootSpace.rpt" "drivenElement_parentConstraint1.tg[2].trt";
connectAttr "rootSpace.r" "drivenElement_parentConstraint1.tg[2].tr";
connectAttr "rootSpace.ro" "drivenElement_parentConstraint1.tg[2].tro";
connectAttr "rootSpace.s" "drivenElement_parentConstraint1.tg[2].ts";
connectAttr "rootSpace.pm" "drivenElement_parentConstraint1.tg[2].tpm";
connectAttr "drivenElement_parentConstraint1.w2" "drivenElement_parentConstraint1.tg[2].tw"
		;
connectAttr "uiConfigurationScriptNode.config" "uiConfigurationScriptNode.b";
// End of toggleParentWeightsSample01.ma
