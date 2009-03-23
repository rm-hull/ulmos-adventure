package rpg.editor.core;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
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
	
    protected Point highlightTile = null;
    protected Point selectedTile = null;
    
    protected Rectangle highlightRectangle = null;
    protected Rectangle selectedRectangle = null;

    protected Point topLeft = new Point(0, 0);
    
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
					if (highlightTile != null) {
						Image highlight = ImageHelper.getHighlightImage(viewSize);
						gc.drawImage(highlight,
								highlightTile.x * tileSize + topLeft.x,
								highlightTile.y * tileSize + topLeft.y);
					}
					if (selectedTile != null) {
						Image selected = ImageHelper.getSelectedImage(viewSize);
						gc.drawImage(selected,
								selectedTile.x * tileSize + topLeft.x,
								selectedTile.y * tileSize + topLeft.y);
					}
					gc.dispose();
				}
			}
		});
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
