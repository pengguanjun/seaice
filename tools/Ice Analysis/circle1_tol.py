import wx
import numpy as np
from imagepy.core.engine import Tool, Filter,Simple
import scipy.ndimage as nimg
from imagepy.core.mark import GeometryMark



class NewTool(Simple):
    para = {'x':0, 'y':0,'r':100,'preview':True,'z':1}
    view = [(int, 'x', (0,1000), 0, 'x', 'pix'),
    (int, 'y', (0,1000), 0, 'y', 'pix'),
    (int, 'r', (0,1000), 0, 'r', 'pix'),
    (int, 'z', (0,1000), 0, 'z', 'pix')
    ]
    # img = '../imgdata/new.png'
    title = 'para'
    note = [ 'all', 'preview']
    body=None
    def load(self, ips=None):
        print('load')
        self.para['x'],self.para['y'],self.para['r']=self.body
        self.para['z']=self.parent.body[1]['z'][self.index]
        return True
    def preview(self, ips, para):
        self.ok(self.ips)
    def run(self, parent, doc, para):
        self.body=(self.para['x'],self.para['y'],self.para['r'])
        self.parent.body[0]['body'][self.index]=self.body
        self.parent.body[1]['body'][self.index]=(self.para['x'],self.para['y'],5)
        # print(self.parent.body[1]['z'],self.index)
        self.parent.body[1]['z'][self.index]=self.para['z']

class Plugin(Tool):
    title = 'circle'

    def __init__(self):
        self.moving = False
        self.body=[{'type':'circles', 'body':[]},{'type':'circles', 'fill':True,'body':[],'z':[]}]
    def mouse_down(self, ips, x, y, btn, **key):   
        flag,i=self.pick(x,y,5.0/key['canvas'].get_scale() )
        if flag==True:
            self.moving = True
            self.move_index=i
        print(key['ctrl'])
        if key['shift']:
            self.add(x,y)
            ips.update = True
            return           
        print('moving',self.moving)
        if self.moving==False:
            self.body[0]['body']=[(x,y,100)]
            self.body[1]['body']=[(x,y,5)]
            self.body[1]['z']=[1]
            self.commit(ips)

        if key['ctrl'] and flag==True:
            # surface2d()
            print('in ui')
            pd = NewTool()
            pd.body=self.body[0]['body'][i]
            pd.parent,pd.index=self,i
            pd.start()  
    def pick(self,x,y,lim):
        for i in range(len(self.body[0]['body'])):
            ox,oy=self.body[0]['body'][i][0],self.body[0]['body'][i][1]
            if abs(x-ox)<lim and abs(y-oy)<lim:return(True,i)
        return (False,-1)
    def add(self,x,y):
        self.body[0]['body'].append((x,y,100))
        self.body[1]['body'].append((x,y,5))
        self.body[1]['z'].append(1)
        print('add',self.body)
    def change(self,index,x=None,y=None,r=None):
        temp=self.body[0]['body'][index]
        if x!=None and y!=None:
            self.body[0]['body'][index]=(x,y,temp[2])
            self.body[1]['body'][index]=(x,y,5)
        elif x!=None:
            self.body[0]['body'][index]=(x,temp[1],temp[2])
            self.body[1]['body'][index]=(x,temp[1],5)
        elif y!=None:
            self.body[0]['body'][index]=(temp[0],y,temp[2])
            self.body[1]['body'][index]=(temp[0],y,5) 
        if r!=None:
            self.body[0]['body'][index]=(temp[0],temp[1],temp[2]+r)                     
    def mouse_up(self, ips, x, y, btn, **key):
        if self.moving : self.moving = False
    def commit(self,ips):
            mark =  {'type':'layers', 'body':{}}
            layer = {'type':'layer', 'body':[]}
            layer['body']=self.body
            mark['body'][0] = layer
            ips.mark=GeometryMark(mark)
            ips.update = True
            ips.data=self.body
    def mouse_move(self, ips, x, y, btn, **key):
        lim = 5.0/key['canvas'].get_scale()
        if btn==None:
            self.cursor = wx.CURSOR_CROSS
            flag,i=self.pick(x,y,5.0/key['canvas'].get_scale() )
            if flag==True:
                self.cursor = wx.CURSOR_HAND
                    # return
        elif self.moving:
            self.change(self.move_index,x=x,y=y)
            self.commit(ips)
            return
    def mouse_wheel(self, ips, x, y, d, **key):
        lim = 5.0/key['canvas'].get_scale()
        flag,i=self.pick(x,y,5.0/key['canvas'].get_scale() )
        if flag==True:
            self.change(i,r=d*5)
            self.commit(ips)