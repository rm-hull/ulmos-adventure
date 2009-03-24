package rpg.editor.core;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;

/**
 * An extended canvas component that displays a collection of tiles.  This forms
 * the basis of the three main components: TilePicker, RecentTiles and MapEditor.
 * @author seldred
 */
public abstract class TileCanvas extends Canvas {
	
    protected Point topLeft = new Point(0, 0);
    
    protected Point highlightTile = null;
    protected Point selectedTile = null;
    
    protected Rectangle highlightRectangle = null;
    protected Rectangle selectedRectangle = null;

	public ViewSize viewSize = ViewSize.MEDIUM;	
	public Image tileImage;
	
	public TileCanvas(Composite parent) {
		this(parent, SWT.NONE);
	}
	
	public TileCanvas(Composite parent, int style) {
		super(parent, style);
		
		// ** paint listener **
		addListener(SWT.Paint, new Listener() {
			public void handleEvent (Event e) {
				if (tileImage != null) {
					Point point = getSize();
					Rectangle rect = tileImage.getBounds();
					topLeft.x = point.x > rect.width ? (point.x - rect.width) / 2 : 0;
					topLeft.y = point.y > rect.height ? (point.y - rect.height) / 2 : 0;
					GC gc = e.gc;
					gc.drawImage(tileImage, topLeft.x, topLeft.y);
					int tileSize = viewSize.getTileSize();
					if (highlightRectangle != null) {
						drawRectangle(gc, highlightRectangle,
								ImageHelper.HIGHLIGHT_COLOUR, tileSize);
					}
					else if (highlightTile != null) {
						drawImage(gc, ImageHelper.getHighlightImage(viewSize),
								highlightTile, tileSize);
					}
					if (selectedRectangle != null) {
						drawRectangle(gc, selectedRectangle,
								ImageHelper.SELECTED_COLOUR, tileSize);
					}
					else if (selectedTile != null) {
						drawImage(gc, ImageHelper.getSelectedImage(viewSize),
								selectedTile, tileSize);
					}
					gc.dispose();
				}
			}
		});
	}
	
	private void drawImage(GC gc, Image image, Point tilePoint, int tileSize) {
		gc.drawImage(image,
				tilePoint.x * tileSize + topLeft.x,
				tilePoint.y * tileSize + topLeft.y);		
	}
	
	// note that this 
	private void drawRectangle(GC gc, Rectangle rect, RGB rgb, int tileSize) {
		gc.setForeground(new Color(DisplayHelper.getDisplay(), rgb));
		int x = rect.x * tileSize + topLeft.x;
		int y = rect.y * tileSize + topLeft.y;
		int width = rect.width * tileSize - 1;
		int height = rect.height * tileSize - 1;
		gc.drawRectangle(x, y, width, height);
		gc.drawRectangle(x + 1, y + 1, width - 2, height - 2);
	}
	
	protected Point determineCurrentTile(MouseEvent e) {
		Rectangle r = tileImage.getBounds();
		if ((e.x > topLeft.x) && (e.x < topLeft.x + r.width)
				&& (e.y > topLeft.y) && (e.y < topLeft.y + r.height)) {
			int tileX = (e.x - topLeft.x) / viewSize.getTileSize();
			int tileY = (e.y - topLeft.y) / viewSize.getTileSize();
			return new Point(tileX, tileY);
		}
		return null;
	}
	
	public abstract void setLabelText();
}
