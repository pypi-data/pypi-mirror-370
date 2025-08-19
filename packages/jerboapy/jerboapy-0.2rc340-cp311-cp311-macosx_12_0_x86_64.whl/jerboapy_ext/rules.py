from jerboapy import *

from .utils import *
from .Point3 import Point3
from .Color4 import Color4



def rule_duplication_Duplicate():
	def fun_n1_pos(context):
		return context.gmap[context.leftdart].ebd123["pos"]
	def fun_n1_color(context):
		return context.gmap[context.leftdart].ebd01["color"]
	def fun_n1_orient(context):
		return context.gmap[context.leftdart].ebd["orient"]
	def fun_n1_normal(context):
		return context.gmap[context.leftdart].ebd01["normal"]
	
	expr_n1_pos = Expr3DEbd123("pos",fun_n1_pos)
	expr_n1_color = Expr3DEbd01("color",fun_n1_color)
	expr_n1_orient = Expr3DEbdDart("orient",fun_n1_orient)
	expr_n1_normal = Expr3DEbd01("normal",fun_n1_normal)
	rule = Rule3D("Duplicate","duplication")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1,2,3], True)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0,1,2,3])
	rn1 = rule.make_rightnode("n1", [0,1,2,3],[expr_n1_pos,expr_n1_color,expr_n1_orient,expr_n1_normal])
	rule.compile()
	return rule

def rule_creat_CreatSquare():
	def fun_n0_pos(context):
		return Point3(0,0,0)
	def fun_n0_color(context):
		return Color4.randomColor()
	def fun_n0_orient(context):
		return True
	def fun_n0_normal(context):
		return  Point3(0,1,0)
	def fun_n1_pos(context):
		return  Point3(1,0,0)
	def fun_n1_orient(context):
		return False
	def fun_n2_orient(context):
		return True
	def fun_n3_pos(context):
		return  Point3(1,0,1)
	def fun_n3_orient(context):
		return False
	def fun_n4_orient(context):
		return True
	def fun_n5_pos(context):
		return  Point3(0,0,1)
	def fun_n5_orient(context):
		return False
	def fun_n6_orient(context):
		return True
	def fun_n7_orient(context):
		return False
	expr_n0_pos = Expr3DEbd123("pos",fun_n0_pos)
	expr_n0_color = Expr3DEbd01("color",fun_n0_color)
	expr_n0_orient = Expr3DEbdDart("orient",fun_n0_orient)
	expr_n0_normal = Expr3DEbd01("normal",fun_n0_normal)
	expr_n1_pos = Expr3DEbd123("pos",fun_n1_pos)
	expr_n1_orient = Expr3DEbdDart("orient",fun_n1_orient)
	expr_n2_orient = Expr3DEbdDart("orient",fun_n2_orient)
	expr_n3_pos = Expr3DEbd123("pos",fun_n3_pos)
	expr_n3_orient = Expr3DEbdDart("orient",fun_n3_orient)
	expr_n4_orient = Expr3DEbdDart("orient",fun_n4_orient)
	expr_n5_pos = Expr3DEbd123("pos",fun_n5_pos)
	expr_n5_orient = Expr3DEbdDart("orient",fun_n5_orient)
	expr_n6_orient = Expr3DEbdDart("orient",fun_n6_orient)
	expr_n7_orient = Expr3DEbdDart("orient",fun_n7_orient)
	rule = Rule3D("CreatSquare","creat")
	# motif gauche 
	# motif droit 
	rn0 = rule.make_rightnode("n0", [],[expr_n0_pos,expr_n0_color,expr_n0_orient,expr_n0_normal])
	rn1 = rule.make_rightnode("n1", [],[expr_n1_pos,expr_n1_orient,expr_n0_normal,expr_n0_color])
	rn2 = rule.make_rightnode("n2", [],[expr_n2_orient,expr_n1_pos,expr_n0_normal,expr_n0_color])
	rn3 = rule.make_rightnode("n3", [],[expr_n3_pos,expr_n3_orient,expr_n0_normal,expr_n0_color])
	rn4 = rule.make_rightnode("n4", [],[expr_n4_orient,expr_n3_pos,expr_n0_normal,expr_n0_color])
	rn5 = rule.make_rightnode("n5", [],[expr_n5_pos,expr_n5_orient,expr_n0_normal,expr_n0_color])
	rn6 = rule.make_rightnode("n6", [],[expr_n6_orient,expr_n5_pos,expr_n0_normal,expr_n0_color])
	rn7 = rule.make_rightnode("n7", [],[expr_n7_orient,expr_n0_pos,expr_n0_normal,expr_n0_color])
	rule.linkRightNodes(0,rn0,rn1)
	rule.linkRightNodes(1,rn1,rn2)
	rule.linkRightNodes(0,rn2,rn3)
	rule.linkRightNodes(1,rn3,rn4)
	rule.linkRightNodes(0,rn4,rn5)
	rule.linkRightNodes(1,rn5,rn6)
	rule.linkRightNodes(0,rn6,rn7)
	rule.linkRightNodes(1,rn7,rn0)
	rule.linkRightNodes(2,rn0,rn0)
	rule.linkRightNodes(3,rn0,rn0)
	rule.linkRightNodes(2,rn1,rn1)
	rule.linkRightNodes(3,rn1,rn1)
	rule.linkRightNodes(2,rn2,rn2)
	rule.linkRightNodes(3,rn2,rn2)
	rule.linkRightNodes(2,rn3,rn3)
	rule.linkRightNodes(3,rn3,rn3)
	rule.linkRightNodes(2,rn4,rn4)
	rule.linkRightNodes(3,rn4,rn4)
	rule.linkRightNodes(2,rn5,rn5)
	rule.linkRightNodes(3,rn5,rn5)
	rule.linkRightNodes(2,rn6,rn6)
	rule.linkRightNodes(3,rn6,rn6)
	rule.linkRightNodes(2,rn7,rn7)
	rule.linkRightNodes(3,rn7,rn7)
	rule.compile()
	return rule

def rule_sew_SewA0():
	rule = Rule3D("SewA0","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [2,3], True)
	ln1 = rule.make_leftnode("n1", [2,3], True)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [2,3])
	rn1 = rule.make_rightnode("n1", [2,3])
	rule.linkRightNodes(0,rn0,rn1)
	rule.compile()
	return rule

def rule_sew_SewA1():
	rule = Rule3D("SewA1","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [3], True)
	ln1 = rule.make_leftnode("n1", [3], True)
	rule.linkLeftNodes(1,ln0,ln0)
	rule.linkLeftNodes(1,ln1,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [3])
	rn1 = rule.make_rightnode("n1", [3])
	rule.linkRightNodes(1,rn0,rn1)
	rule.compile()
	return rule

def rule_sew_SewA2():
	rule = Rule3D("SewA2","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0], True)
	ln1 = rule.make_leftnode("n1", [0], True)
	rule.linkLeftNodes(2,ln0,ln0)
	rule.linkLeftNodes(2,ln1,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0])
	rn1 = rule.make_rightnode("n1", [0])
	rule.linkRightNodes(2,rn0,rn1)
	rule.compile()
	return rule

def rule_sew_SewA3():
	rule = Rule3D("SewA3","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1], True)
	ln1 = rule.make_leftnode("n1", [0,1], True)
	rule.linkLeftNodes(3,ln0,ln0)
	rule.linkLeftNodes(3,ln1,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0,1])
	rn1 = rule.make_rightnode("n1", [0,1])
	rule.linkRightNodes(3,rn0,rn1)
	rule.compile()
	return rule

def rule_sew_UnSewA0():
	rule = Rule3D("UnSewA0","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [2,3], True)
	ln1 = rule.make_leftnode("n1", [2,3])
	rule.linkLeftNodes(0,ln0,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [2,3])
	rn1 = rule.make_rightnode("n1", [2,3])
	rule.linkRightNodes(0,rn1,rn1)
	rule.linkRightNodes(0,rn0,rn0)
	rule.compile()
	return rule

def rule_sew_UnSewA1():
	rule = Rule3D("UnSewA1","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [3], True)
	ln1 = rule.make_leftnode("n1", [3])
	rule.linkLeftNodes(1,ln0,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [3])
	rn1 = rule.make_rightnode("n1", [3])
	rule.linkRightNodes(1,rn0,rn0)
	rule.linkRightNodes(1,rn1,rn1)
	rule.compile()
	return rule

def rule_sew_UnSewA2():
	rule = Rule3D("UnSewA2","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0], True)
	ln1 = rule.make_leftnode("n1", [0])
	rule.linkLeftNodes(2,ln0,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0])
	rn1 = rule.make_rightnode("n1", [0])
	rule.linkRightNodes(2,rn0,rn0)
	rule.linkRightNodes(2,rn1,rn1)
	rule.compile()
	return rule

def rule_sew_UnSewA3():
	rule = Rule3D("UnSewA3","sew")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1], True)
	ln1 = rule.make_leftnode("n1", [0,1])
	rule.linkLeftNodes(3,ln0,ln1)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0,1])
	rn1 = rule.make_rightnode("n1", [0,1])
	rule.linkRightNodes(3,rn1,rn1)
	rule.linkRightNodes(3,rn0,rn0)
	rule.compile()
	return rule




def rule_subdivision_DooSabin3D():
	def fun_n0_pos(context):
		points = collect123([0,1,2], context.gmap, context.leftdart, "pos", Point3(0,0,0))
		centerFace = Point3.middle(points)
		res = Point3.middle(centerFace, context.gmap[context.leftdart].ebd123["pos"])
		return res
	def fun_n1_color(context):
		return Color4.randomColor()
	def fun_n1_orient(context):
		return not context.gmap[context.leftdart].ebd["orient"]
	def fun_n2_orient(context):
		return context.gmap[context.leftdart].ebd["orient"]
	def fun_n2_normal(context):
		vec =  Point3()
		vec.add(context.gmap[context.leftdart].ebd01["normal"])
		voisin = context.gmap[context.leftdart].alpha(2)
		vec.add(context.gmap[voisin].ebd01["normal"])
		vec.normalize()
		return vec
	def fun_n3_color(context):
		return Color4.randomColor()
	def fun_n3_orient(context):
		return not context.gmap[context.leftdart].ebd["orient"]
	def fun_n3_normal(context):
		normals = collect01([1,2,3], context.gmap, context.leftdart, "normal", Point3(0,0,0))
		resnorm = Point3.sum(normals)
		resnorm.normalize()
		return resnorm
	expr_n0_pos = Expr3DEbd123("pos",fun_n0_pos)
	expr_n1_color = Expr3DEbd01("color",fun_n1_color)
	expr_n1_orient = Expr3DEbdDart("orient",fun_n1_orient)
	expr_n2_orient = Expr3DEbdDart("orient",fun_n2_orient)
	expr_n2_normal = Expr3DEbd01("normal",fun_n2_normal)
	expr_n3_color = Expr3DEbd01("color",fun_n3_color)
	expr_n3_orient = Expr3DEbdDart("orient",fun_n3_orient)
	expr_n3_normal = Expr3DEbd01("normal",fun_n3_normal)
	rule = Rule3D("DooSabin3D","subdivision")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1,2,3], True)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0,1,-1,3],[expr_n0_pos])
	rn1 = rule.make_rightnode("n1", [0,-1,-1,-1],[expr_n1_color,expr_n1_orient,expr_n0_pos,expr_n2_normal])
	rn2 = rule.make_rightnode("n2", [-1,-1,0,-1],[expr_n2_orient,expr_n2_normal,expr_n0_pos,expr_n1_color])
	rn3 = rule.make_rightnode("n3", [-1,1,0,-1],[expr_n3_color,expr_n3_orient,expr_n3_normal,expr_n0_pos])
	rule.linkRightNodes(2,rn0,rn1)
	rule.linkRightNodes(1,rn1,rn2)
	rule.linkRightNodes(2,rn2,rn3)
	rule.linkRightNodes(3,rn1,rn1)
	rule.linkRightNodes(3,rn2,rn2)
	rule.linkRightNodes(3,rn3,rn3)
	rule.compile()
	return rule

def rule_subdivision_Menger3D_casse():
	def fun_n1_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n1_pos(context):
		print(">>> fun_n1_pos ", context.leftdart)
		voisin = context.leftdart.alpha(0)
		return Point3.linear(context.leftdart.ebd123["pos"], voisin.ebd123["pos"], 1.0/3.0)
	def fun_n2_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n3_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n4_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n4_normal(context):
		voisin = context.gmap.path(context.leftdart, [1,2])
		resnorm =  context.gmap[voisin].ebd.get("normal", Point3(0,0,1))
		resnorm.scale(-1.0)
		return resnorm
	def fun_n5_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n5_normal(context):
		voisin = context.gmap.path(context.leftdart, [1,2])
		resnorm =  context.gmap[voisin].ebd.get("normal", Point3(0,0,1))
		return resnorm
		
	def fun_n6_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n6_normal(context):
		return context.gmap[context.leftdart].ebd01["normal"]
	def fun_n7_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n7_pos(context):
		n0a0 = context.gmap[context.leftdart].alpha(0)
		a =  context.gmap[n0a0].ebd123["pos"].sub(context.gmap[context.leftdart].ebd123["pos"])
		n0a1a0 = context.gmap.path(context.leftdart, [1,0])
		b =  context.gmap[n0a1a0].ebd123["pos"].sub(context.gmap[context.leftdart].ebd123["pos"])
		a.add(b)
		a.scale(1.0/3.0)
		a.add(context.gmap[context.leftdart].ebd123["pos"])
		return a
	def fun_n8_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n9_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n10_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n11_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n12_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n12_normal(context):
		n0a2 = context.gmap[context.leftdart].alpha(2)
		# print(">>> n0a2 : ", n0a2)
		resnorm =  context.gmap[n0a2].ebd01["normal"]
		# print(">>> resnorm : ", resnorm)
		# resnorm.scale(-1.0) # ENCORE UN PROBLEME PAS COMPRIS
		return resnorm
	def fun_n13_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n14_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n15_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n16_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n17_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n18_orient(context):
		return context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n19_orient(context):
		return not context.gmap[context.leftdart].ebd.get("orient", True)
	def fun_n19_pos(context):
		n0a0 = context.gmap[context.leftdart].alpha(0)
		n0a1a0 = context.gmap.path(context.leftdart, [1,0])
		n0a2a1a0 = context.gmap.path(context.leftdart, [2,1,0])
		a =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a0].ebd123["pos"])
		b =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a1a0].ebd123["pos"])
		c =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a2a1a0].ebd123["pos"])
		a.add(b)
		a.add(c)
		a.scale(1.0/3.0)
		a.add(context.gmap[context.leftdart].ebd123["pos"])
		
		return a
		
	expr_n1_orient = Expr3DEbdDart("orient",fun_n1_orient)
	expr_n1_pos = Expr3DEbd123("pos",fun_n1_pos)
	expr_n2_orient = Expr3DEbdDart("orient",fun_n2_orient)
	expr_n3_orient = Expr3DEbdDart("orient",fun_n3_orient)
	expr_n4_orient = Expr3DEbdDart("orient",fun_n4_orient)
	expr_n4_normal = Expr3DEbd01("normal",fun_n4_normal)
	expr_n5_orient = Expr3DEbdDart("orient",fun_n5_orient)
	expr_n5_normal = Expr3DEbd01("normal",fun_n5_normal)
	expr_n6_orient = Expr3DEbdDart("orient",fun_n6_orient)
	expr_n6_normal = Expr3DEbd01("normal",fun_n6_normal)
	expr_n7_orient = Expr3DEbdDart("orient",fun_n7_orient)
	expr_n7_pos = Expr3DEbd123("pos",fun_n7_pos)
	expr_n8_orient = Expr3DEbdDart("orient",fun_n8_orient)
	expr_n9_orient = Expr3DEbdDart("orient",fun_n9_orient)
	expr_n10_orient = Expr3DEbdDart("orient",fun_n10_orient)
	expr_n11_orient = Expr3DEbdDart("orient",fun_n11_orient)
	expr_n12_orient = Expr3DEbdDart("orient",fun_n12_orient)
	expr_n12_normal = Expr3DEbd01("normal",fun_n12_normal)
	expr_n13_orient = Expr3DEbdDart("orient",fun_n13_orient)
	expr_n14_orient = Expr3DEbdDart("orient",fun_n14_orient)
	expr_n15_orient = Expr3DEbdDart("orient",fun_n15_orient)
	expr_n16_orient = Expr3DEbdDart("orient",fun_n16_orient)
	expr_n17_orient = Expr3DEbdDart("orient",fun_n17_orient)
	expr_n18_orient = Expr3DEbdDart("orient",fun_n18_orient)
	expr_n19_orient = Expr3DEbdDart("orient",fun_n19_orient)
	expr_n19_pos = Expr3DEbd123("pos",fun_n19_pos)
	rule = Rule3D("Menger3D","subdivision")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1,2,3], True)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [-1,1,2,3])
	rn1 = rule.make_rightnode("n1", [-1,-1,2,3],[expr_n1_orient,expr_n1_pos])
	rn2 = rule.make_rightnode("n2", [0,-1,2,3],[expr_n2_orient,expr_n1_pos,expr_n6_normal])
	rn3 = rule.make_rightnode("n3", [-1,-1,-1,3],[expr_n3_orient,expr_n1_pos])
	rn4 = rule.make_rightnode("n4", [-1,-1,1,-1],[expr_n4_orient,expr_n4_normal,expr_n1_pos])
	rn5 = rule.make_rightnode("n5", [-1,-1,1,-1],[expr_n5_orient,expr_n5_normal,expr_n1_pos])
	rn6 = rule.make_rightnode("n6", [-1,-1,-1,3],[expr_n6_orient,expr_n6_normal,expr_n1_pos])
	rn7 = rule.make_rightnode("n7", [-1,1,-1,3],[expr_n7_orient,expr_n7_pos])
	rn8 = rule.make_rightnode("n8", [-1,-1,-1,-1],[expr_n8_orient,expr_n7_pos,expr_n4_normal])
	rn9 = rule.make_rightnode("n9", [-1,-1,-1,-1],[expr_n9_orient,expr_n7_pos,expr_n5_normal])
	rn10 = rule.make_rightnode("n10", [-1,-1,-1,3],[expr_n10_orient,expr_n7_pos,expr_n6_normal])
	rn11 = rule.make_rightnode("n11", [0,-1,-1,3],[expr_n11_orient,expr_n7_pos,expr_n6_normal])
	rn12 = rule.make_rightnode("n12", [0,-1,-1,-1],[expr_n12_orient,expr_n12_normal,expr_n7_pos])
	rn13 = rule.make_rightnode("n13", [-1,2,-1,-1],[expr_n13_orient,expr_n7_pos,expr_n4_normal])
	rn14 = rule.make_rightnode("n14", [-1,-1,-1,-1],[expr_n14_orient,expr_n7_pos,expr_n5_normal])
	rn15 = rule.make_rightnode("n15", [-1,-1,-1,-1],[expr_n15_orient,expr_n7_pos,expr_n12_normal])
	rn16 = rule.make_rightnode("n16", [-1,2,1,-1],[expr_n16_orient,expr_n19_pos,expr_n4_normal])
	rn17 = rule.make_rightnode("n17", [-1,-1,1,-1],[expr_n17_orient,expr_n19_pos,expr_n5_normal])
	rn18 = rule.make_rightnode("n18", [-1,-1,-1,-1],[expr_n18_orient,expr_n19_pos,expr_n12_normal])
	rn19 = rule.make_rightnode("n19", [0,-1,2,-1],[expr_n19_orient,expr_n19_pos,expr_n12_normal])
	rule.linkRightNodes(0,rn0,rn1)
	rule.linkRightNodes(1,rn1,rn3)
	rule.linkRightNodes(0,rn3,rn7)
	rule.linkRightNodes(2,rn3,rn4)
	rule.linkRightNodes(2,rn7,rn8)
	rule.linkRightNodes(0,rn4,rn8)
	rule.linkRightNodes(0,rn5,rn9)
	rule.linkRightNodes(0,rn6,rn10)
	rule.linkRightNodes(1,rn8,rn13)
	rule.linkRightNodes(1,rn9,rn14)
	rule.linkRightNodes(1,rn2,rn6)
	rule.linkRightNodes(2,rn6,rn5)
	rule.linkRightNodes(1,rn10,rn11)
	rule.linkRightNodes(2,rn11,rn12)
	rule.linkRightNodes(0,rn15,rn18)
	rule.linkRightNodes(0,rn14,rn17)
	rule.linkRightNodes(0,rn13,rn16)
	rule.linkRightNodes(1,rn15,rn12)
	rule.linkRightNodes(2,rn14,rn15)
	rule.linkRightNodes(2,rn17,rn18)
	rule.linkRightNodes(3,rn14,rn13)
	rule.linkRightNodes(3,rn17,rn16)
	rule.linkRightNodes(3,rn8,rn9)
	rule.linkRightNodes(3,rn5,rn4)
	rule.linkRightNodes(2,rn9,rn10)
	rule.linkRightNodes(1,rn18,rn19)
	rule.linkRightNodes(3,rn19,rn19)
	rule.linkRightNodes(3,rn18,rn18)
	rule.linkRightNodes(3,rn15,rn15)
	rule.linkRightNodes(3,rn12,rn12)
	rule.compile()
	return rule


def rule_subdivision_Menger3D():
	def fun_nX_color(context):
		return context.leftdart.ebd01.get("color", Color4.GRAY)
	def fun_n1_pos(context):
		voisin = context.gmap[context.leftdart].alpha(0)
		return Point3.linear(context.gmap[context.leftdart].ebd123["pos"], context.gmap[voisin].ebd123["pos"], 1.0/3.0)
	def fun_n7_pos(context):
		n0a0 = context.gmap[context.leftdart].alpha(0)
		a =  context.gmap[n0a0].ebd123["pos"].sub(context.gmap[context.leftdart].ebd123["pos"])
		n0a1a0 = context.gmap.path(context.leftdart, [1,0])
		b =  context.gmap[n0a1a0].ebd123["pos"].sub(context.gmap[context.leftdart].ebd123["pos"])
		a = a.add(b)
		a = a.scale(1.0/3.0)
		a = a.add(context.gmap[context.leftdart].ebd123["pos"])
		return a
	def fun_n19_pos(context):
		n0a0 = context.gmap[context.leftdart].alpha(0)
		n0a1a0 = context.gmap.path(context.leftdart, [1,0])
		n0a2a1a0 = context.gmap.path(context.leftdart, [2,1,0])
		a =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a0].ebd123["pos"])
		b =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a1a0].ebd123["pos"])
		c =  Point3(context.gmap[context.leftdart].ebd123["pos"], context.gmap[n0a2a1a0].ebd123["pos"])
		a = a.add(b)
		a = a.add(c)
		a = a.scale(1.0/3.0)
		a = a.add(context.gmap[context.leftdart].ebd123["pos"])
		
		return a
		
	expr_n1_pos = Expr3DEbd123("pos",fun_n1_pos)
	expr_n7_pos = Expr3DEbd123("pos",fun_n7_pos)
	expr_n19_pos = Expr3DEbd123("pos",fun_n19_pos)
	expr_nX_color = Expr3DEbd01("color",fun_nX_color)

	rule = Rule3D("Menger3D","subdivision")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1,2,3], True)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [-1,1,2,3])
	rn1 = rule.make_rightnode("n1", [-1,-1,2,3],[expr_n1_pos,expr_nX_color])
	rn2 = rule.make_rightnode("n2", [0,-1,2,3],[expr_n1_pos,expr_nX_color])
	rn3 = rule.make_rightnode("n3", [-1,-1,-1,3],[expr_n1_pos,expr_nX_color])
	rn4 = rule.make_rightnode("n4", [-1,-1,1,-1],[expr_n1_pos,expr_nX_color])
	rn5 = rule.make_rightnode("n5", [-1,-1,1,-1],[expr_n1_pos,expr_nX_color])
	rn6 = rule.make_rightnode("n6", [-1,-1,-1,3],[expr_n1_pos,expr_nX_color])
	rn7 = rule.make_rightnode("n7", [-1,1,-1,3],[expr_n7_pos,expr_nX_color])
	rn8 = rule.make_rightnode("n8", [-1,-1,-1,-1],[expr_n7_pos,expr_nX_color])
	rn9 = rule.make_rightnode("n9", [-1,-1,-1,-1],[expr_n7_pos,expr_nX_color])
	rn10 = rule.make_rightnode("n10", [-1,-1,-1,3],[expr_n7_pos,expr_nX_color])
	rn11 = rule.make_rightnode("n11", [0,-1,-1,3],[expr_n7_pos,expr_nX_color])
	rn12 = rule.make_rightnode("n12", [0,-1,-1,-1],[expr_n7_pos,expr_nX_color])
	rn13 = rule.make_rightnode("n13", [-1,2,-1,-1],[expr_n7_pos,expr_nX_color])
	rn14 = rule.make_rightnode("n14", [-1,-1,-1,-1],[expr_n7_pos,expr_nX_color])
	rn15 = rule.make_rightnode("n15", [-1,-1,-1,-1],[expr_n7_pos,expr_nX_color])
	rn16 = rule.make_rightnode("n16", [-1,2,1,-1],[expr_n19_pos,expr_nX_color])
	rn17 = rule.make_rightnode("n17", [-1,-1,1,-1],[expr_n19_pos,expr_nX_color])
	rn18 = rule.make_rightnode("n18", [-1,-1,-1,-1],[expr_n19_pos,expr_nX_color])
	rn19 = rule.make_rightnode("n19", [0,-1,2,-1],[expr_n19_pos,expr_nX_color])
	rule.linkRightNodes(0,rn0,rn1)
	rule.linkRightNodes(1,rn1,rn3)
	rule.linkRightNodes(0,rn3,rn7)
	rule.linkRightNodes(2,rn3,rn4)
	rule.linkRightNodes(2,rn7,rn8)
	rule.linkRightNodes(0,rn4,rn8)
	rule.linkRightNodes(0,rn5,rn9)
	rule.linkRightNodes(0,rn6,rn10)
	rule.linkRightNodes(1,rn8,rn13)
	rule.linkRightNodes(1,rn9,rn14)
	rule.linkRightNodes(1,rn2,rn6)
	rule.linkRightNodes(2,rn6,rn5)
	rule.linkRightNodes(1,rn10,rn11)
	rule.linkRightNodes(2,rn11,rn12)
	rule.linkRightNodes(0,rn15,rn18)
	rule.linkRightNodes(0,rn14,rn17)
	rule.linkRightNodes(0,rn13,rn16)
	rule.linkRightNodes(1,rn15,rn12)
	rule.linkRightNodes(2,rn14,rn15)
	rule.linkRightNodes(2,rn17,rn18)
	rule.linkRightNodes(3,rn14,rn13)
	rule.linkRightNodes(3,rn17,rn16)
	rule.linkRightNodes(3,rn8,rn9)
	rule.linkRightNodes(3,rn5,rn4)
	rule.linkRightNodes(2,rn9,rn10)
	rule.linkRightNodes(1,rn18,rn19)
	rule.linkRightNodes(3,rn19,rn19)
	rule.linkRightNodes(3,rn18,rn18)
	rule.linkRightNodes(3,rn15,rn15)
	rule.linkRightNodes(3,rn12,rn12)
	rule.compile()
	return rule


def rule_extrude_ExtrudeFace():
	def fun_n0_normal(context):
		n =  context.leftdart.ebd01["normal"].copy()
		n.scale(-1)
		return n
	def fun_n1_orient(context):
		return not context.leftdart.ebd["orient"]
	def fun_n1_normal(context):
		d = context.leftdart
		if(not d.ebd['orient']):
			d = d.alpha(0)
		e =  d.a(0).ebd123["pos"] - d.ebd123["pos"]
		e.normalize()
		return context.leftdart.ebd01["normal"].cross(e)
	def fun_n2_orient(context):
		return context.leftdart.ebd["orient"]
	def fun_n3_orient(context):
		return not context.leftdart.ebd["orient"]
	def fun_n4_orient(context):
		return context.leftdart.ebd["orient"]
	def fun_n5_orient(context):
		return not context.leftdart.ebd["orient"]
	def fun_n5_normal(context):
		return context.leftdart.ebd01["normal"]
	def fun_n5_pos(context):
		# print(f">>> fun_n5_pos leftdart={context.leftdart} rightdart={context.rightdart} pos={context.leftdart.ebd123['pos']} normal={context.leftdart.ebd01['normal']}")
		pos = context.leftdart.ebd123["pos"]
		normal = context.leftdart.ebd01["normal"]
		return pos + normal
	def fun_n0_pos(context):
		return context.leftdart.ebd123["pos"]
	expr_n0_normal = Expr3DEbd01("normal",fun_n0_normal)
	expr_n1_orient = Expr3DEbdDart("orient",fun_n1_orient)
	expr_n1_normal = Expr3DEbd01("normal",fun_n1_normal)
	expr_n2_orient = Expr3DEbdDart("orient",fun_n2_orient)
	expr_n3_orient = Expr3DEbdDart("orient",fun_n3_orient)
	expr_n4_orient = Expr3DEbdDart("orient",fun_n4_orient)
	expr_n5_orient = Expr3DEbdDart("orient",fun_n5_orient)
	expr_n5_normal = Expr3DEbd01("normal",fun_n5_normal)
	expr_n5_pos = Expr3DEbd123("pos",fun_n5_pos)
	expr_n0_pos = Expr3DEbd123("pos",fun_n0_pos)
	rule = Rule3D("SolExtrudeFace","solution")
	# motif gauche 
	ln0 = rule.make_leftnode("n0", [0,1], True)
	rule.linkLeftNodes(2,ln0,ln0)
	# motif droit 
	rn0 = rule.make_rightnode("n0", [0,1],[expr_n0_normal])
	rn1 = rule.make_rightnode("n1", [0,-1],[expr_n1_orient,expr_n1_normal, expr_n0_pos])
	rn2 = rule.make_rightnode("n2", [-1,2],[expr_n2_orient,expr_n1_normal, expr_n0_pos])
	rn3 = rule.make_rightnode("n3", [-1,2],[expr_n3_orient,expr_n5_pos,expr_n1_normal])
	rn4 = rule.make_rightnode("n4", [0,-1],[expr_n4_orient,expr_n5_pos,expr_n1_normal])
	rn5 = rule.make_rightnode("n5", [0,1],[expr_n5_orient,expr_n5_normal,expr_n5_pos])
	rule.linkRightNodes(2,rn0,rn1)
	rule.linkRightNodes(1,rn1,rn2)
	rule.linkRightNodes(0,rn2,rn3)
	rule.linkRightNodes(1,rn3,rn4)
	rule.linkRightNodes(3,rn4,rn4)
	rule.linkRightNodes(3,rn3,rn3)
	rule.linkRightNodes(3,rn2,rn2)
	rule.linkRightNodes(3,rn1,rn1)
	rule.linkRightNodes(2,rn4,rn5)
	rule.linkRightNodes(3,rn5,rn5)
	rule.compile()
	return rule
