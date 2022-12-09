// See https://aka.ms/new-console-template for more information
Console.WriteLine("Draw Square!");
DrawSquare(100,100,50,5);
Console.WriteLine("Done!");

static void DrawSquare(int x, int y, int w, int h){
    int xw = x + w;
    int yh = y + h;

    DrawLine(x,y,xw,y);
    DrawLine(xw,y,xw,yh);
    DrawLine(xw,yh,x,yh);
    DrawLine(x,yh,x,y);
}

static void DrawLine(int x1, int y1, int x2, int y2){
    // TODO: 
    DrawSquare(x1,y1,x2,y2);
}