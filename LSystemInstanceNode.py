# randomNode.py
#   Produces random locations to be used with the Maya instancer node.

import sys
import random
import LSystem

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

# Useful functions for declaring attributes as inputs or outputs.
def MAKE_INPUT(attr):
    attr.setKeyable(True)
    attr.setStorable(True)
    attr.setReadable(True)
    attr.setWritable(True)
def MAKE_OUTPUT(attr):
    attr.setKeyable(False)
    attr.setStorable(False)
    attr.setReadable(True)
    attr.setWritable(False)

# Define the name of the node
kPluginNodeTypeName = "LSystemInstanceNode"

# Give the node a unique ID. Make sure this ID is different from all of your
# other nodes!
LSystemInstanceNode = OpenMaya.MTypeId(0x8704)

# Node definition
class LSystemInstanceNode(OpenMayaMPx.MPxNode):
    # Declare class variables:
    # TODO:: declare the input and output class variables
    #         i.e. inNumPoints = OpenMaya.MObject()
    
    angle = OpenMaya.MObject()
    stepSize = OpenMaya.MObject()
    grammarFile = OpenMaya.MObject()
    iterations = OpenMaya.MObject()
    
    outputBranches = OpenMaya.MObject()
    outputFlowers = OpenMaya.MObject()


    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        # TODO:: create the main functionality of the node. Your node should 
        #         take in three floats for max position (X,Y,Z), three floats 
        #         for min position (X,Y,Z), and the number of random points to
        #         be generated. Your node should output an MFnArrayAttrsData 
        #         object containing the random points. Consult the homework
        #         sheet for how to deal with creating the MFnArrayAttrsData. 

        #input data
        angleData = data.inputValue(LSystemInstanceNode.angle);
        stepSizeData = data.inputValue(LSystemInstanceNode.stepSize);
        grammarFileData = data.inputValue(LSystemInstanceNode.grammarFile);
        iterData = data.inputValue(LSystemInstanceNode.iterations);

        angleValue = angleData.asDouble();
        stepSizeValue = stepSizeData.asDouble();
        grammarFileValue = grammarFileData.asString();
        iterValue = iterData.asInt();
       
        #output data
        outBranchesData = data.outputValue(LSystemInstanceNode.outputBranches);
        outBranchesAAD = OpenMaya.MFnArrayAttrsData();
        outBranchesObject = outBranchesAAD.create();
       
        outFlowersData = data.outputValue(LSystemInstanceNode.outputFlowers);
        outFlowersAAD = OpenMaya.MFnArrayAttrsData();
        outFlowersObject = outFlowersAAD.create();

        #vectors for pos, id, scale, aim for branches and flowers
        branchPosArr = outBranchesAAD.vectorArray("position");
        branchIDArr = outBranchesAAD.doubleArray("id");
        branchScaleArr = outBranchesAAD.vectorArray("scale");
        branchAimArr = outBranchesAAD.vectorArray("aimDirection");

        flowerPosArr = outFlowersAAD.vectorArray("position");
        flowerIDArr = outFlowersAAD.doubleArray("id");
        flowerScaleArr = outFlowersAAD.vectorArray("scale");
        flowerAimArr = outFlowersAAD.vectorArray("aimDirection");

        lsystem = LSystem.LSystem();
        lsystem.loadProgram(str(grammarFileValue));
        lsystem.setDefaultAngle(angleValue);
        lsystem.setDefaultStep(stepSizeValue);

        branches = LSystem.VectorPyBranch();
        flowers = LSystem.VectorPyBranch();
    
        for i in range (0, iterValue) :
            currIter = lsystem.getIteration(i);
            lsystem.processPy(i, branches, flowers);

        # fill branches and flowers 
        for j,branch in enumerate(branches):
            start = OpenMaya.MVector(branch[0],branch[2],branch[1]); # switch z and y
            end = OpenMaya.MVector(branch[3],branch[5],branch[4]);
            aim = end - start;
            branchPosArr.append(end);
            branchIDArr.append(j);
            branchScaleArr.append(OpenMaya.MVector(1,1,1));
            branchAimArr.append(aim);

        for k,flower in enumerate(flowers):
            pos = OpenMaya.MVector(flower[0], flower[2], flower[1]);      
            flowerPosArr.append(pos);
            flowerIDArr.append(k);
            flowerScaleArr.append(OpenMaya.MVector(1,1,1));
            flowerAimArr.append(OpenMaya.MVector(1,1,1));


        outBranchesData.setMObject(outBranchesObject);
        outFlowersData.setMObject(outFlowersObject);
        data.setClean(plug)
    
# initializer
def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute();
    nAttr = OpenMaya.MFnNumericAttribute();

    # TODO:: initialize the input and output attributes. Be sure to use the 
    #         MAKE_INPUT and MAKE_OUTPUT functions.
    

    LSystemInstanceNode.angle = nAttr.create("angle", "a", OpenMaya.MFnNumericData.kDouble, 0.0);
    MAKE_INPUT(nAttr);
    LSystemInstanceNode.stepSize = nAttr.create("stepSize", "ss", OpenMaya.MFnNumericData.kDouble, 0.0);
    MAKE_INPUT(nAttr);
    LSystemInstanceNode.grammarFile = tAttr.create("grammarFile", "g", OpenMaya.MFnData.kString);
    MAKE_INPUT(nAttr);
    LSystemInstanceNode.iterations = nAttr.create("iterations", "i", OpenMaya.MFnNumericData.kDouble, 0.0);
    MAKE_INPUT(nAttr);
        
    LSystemInstanceNode.outputBranches = tAttr.create("outputBranches", "ob", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs);
    MAKE_OUTPUT(tAttr);
    LSystemInstanceNode.outputFlowers = tAttr.create("outputFlowers", "of", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs);
    MAKE_OUTPUT(tAttr);

    try:
        # TODO:: add the attributes to the node and set up the
        #         attributeAffects (addAttribute, and attributeAffects)
        print "Initialization!\n"

        LSystemInstanceNode.addAttribute(LSystemInstanceNode.angle);
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.stepSize);
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.iterations);
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.grammarFile);
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.outputBranches);     
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.outputFlowers);        

        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle,LSystemInstanceNode.outputBranches);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle,LSystemInstanceNode.outputFlowers);   
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.stepSize,LSystemInstanceNode.outputBranches);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.stepSize,LSystemInstanceNode.outputFlowers);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations,LSystemInstanceNode.outputBranches);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations,LSystemInstanceNode.outputFlowers);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile,LSystemInstanceNode.outputBranches);
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile,LSystemInstanceNode.outputFlowers);
        

        
    except:
        sys.stderr.write( ("Failed to create attributes of %s node\n", kPluginNodeTypeName) )

# creator
def nodeCreator():
    return OpenMayaMPx.asMPxPtr( LSystemInstanceNode() )




# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( kPluginNodeTypeName, LSystemInstanceNode, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( LSystemInstanceNode )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
