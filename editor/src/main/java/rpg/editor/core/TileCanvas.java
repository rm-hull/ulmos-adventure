package rpg.editor.core;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseMoveListener;
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
	
	protected static final Point NO_SELECTION = new Point(-1, -1);
	
    protected Point highlightTile = NO_SELECTION;
    protected Point selectedTile = NO_SELECTION;

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
					if (!highlightTile.equals(NO_SELECTION)) {
						Image highlight = ImageHelper.getHighlightImage(viewSize);
						gc.drawImage(highlight,
								highlightTile.x * tileSize + topLeft.x,
								highlightTile.y * tileSize + topLeft.y);
					}
					if (!selectedTile.equals(NO_SELECTION)) {
						Image selected = ImageHelper.getSelectedImage(viewSize);
						gc.drawImage(selected,
								selectedTile.x * tileSize + topLeft.x,
								selectedTile.y * tileSize + topLeft.y);
					}
					gc.dispose();
				}
			}
		});
		
		// ** mouse move listener **
		addMouseMoveListener(new MouseMoveListener() {
			public void mouseMove(MouseEvent e) {
				if (tileImage != null) {
					Point previousHighlightTile = highlightTile;
					Rectangle r = tileImage.getBounds();
					if ((e.x > topLeft.x) && (e.x < topLeft.x + r.width)
							&& (e.y > topLeft.y) && (e.y < topLeft.y + r.height)) {
						int tileX = (e.x - topLeft.x) / viewSize.getTileSize();
						int tileY = (e.y - topLeft.y) / viewSize.getTileSize();
						highlightTile = new Point(tileX, tileY);
					}
					else {
						highlightTile = NO_SELECTION;
					}
					if (!highlightTile.equals(previousHighlightTile)) {
						redraw();
						setLabelText();
					}					
				}
			}
		});
	}
	
	public abstract void setLabelText();
}
