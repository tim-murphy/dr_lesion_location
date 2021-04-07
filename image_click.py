# modified from https://stackoverflow.com/questions/5501192/how-to-display-picture-and-get-mouse-click-coordinate-on-it
import wx
import sys
import os

class MyCanvas(wx.ScrolledWindow):
    # position of the optic nerve (from click) - None if not set
    onPos = None
    filepath = None

    def __init__(self, parent, id = -1, size = wx.DefaultSize, filepath = None):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.filepath = os.path.basename(filepath)
        self.image = wx.Image(filepath)
        self.w = self.image.GetWidth()
        self.h = self.image.GetHeight()
        self.bmp = wx.Bitmap(self.image)

        self.SetVirtualSize((self.w, self.h))
        self.SetScrollRate(20,20)
        self.SetBackgroundColour(wx.Colour(0,0,0))

        self.buffer = wx.Bitmap(self.w, self.h)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DoDrawing(dc)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)

    def OnClick(self, event):
        pos = self.CalcUnscrolledPosition(event.GetPosition())
        if (self.onPos == None):
            self.onPos = pos
        else:
            print(self.filepath, self.onPos.x, self.onPos.y, pos.x, pos.y, sep=',')
            self.onPos = None

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    def DoDrawing(self, dc):
        dc.DrawBitmap(self.bmp, 0, 0)

class MyFrame(wx.Frame): 
    def __init__(self, parent=None, id=-1, filepath = None): 
        wx.Frame.__init__(self, parent, id, title=filepath)
        self.canvas = MyCanvas(self, -1, filepath = filepath)

        self.canvas.SetMinSize((self.canvas.w, self.canvas.h))
        self.canvas.SetMaxSize((self.canvas.w, self.canvas.h))
        self.canvas.SetBackgroundColour(wx.Colour(0, 0, 0))
        vert = wx.BoxSizer(wx.VERTICAL)
        horz = wx.BoxSizer(wx.HORIZONTAL)
        vert.Add(horz,0, wx.EXPAND,0)
        vert.Add(self.canvas,1,wx.EXPAND,0)
        self.SetSizer(vert)
        vert.Fit(self)
        self.Layout()

if __name__ == '__main__':
    app = wx.App()
    app.SetOutputWindowAttributes(title='stdout')  
    wx.InitAllImageHandlers()
    
    # data output header
    print("file,onX,onY,macX,macY")

    for i, arg in enumerate(sys.argv):
        # ignore the first argument
        if (i == 0):
            continue
        myframe = MyFrame(filepath=arg)
        myframe.Center()
        myframe.Show()
        app.MainLoop()