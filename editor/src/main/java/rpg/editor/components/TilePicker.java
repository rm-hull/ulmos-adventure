package rpg.editor.components;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.ImageHelper;
import rpg.editor.core.TilePickerCanvas;
import rpg.editor.core.TileSelection;
import rpg.editor.core.TileSelectionStub;
import rpg.editor.core.ViewSize;
import rpg.editor.model.Tile;
import rpg.editor.model.TileSet;

/**
 * Component that allows the user to pick a tile from a TileSet.
 * @author seldred
 */
public class TilePicker extends Composite {
	
	private TileSelection tileSelection;
    
	private TileSet tileSet;
    
    private ScrolledComposite canvasHolder;
    private Label tileLabel;
    
    private TilePickerCanvas tilePickerCanvas;
    
	public TilePicker(Composite parent, TileSet tileSet) {
		this(parent, SWT.NONE, tileSet);
	}
    
	public TilePicker(Composite parent, int style, TileSet tileSet) {

		super(parent, style);
		this.tileSet = tileSet;
				
		// layout setup
		setLayout(new GridLayout());
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
	    // radio buttons
	    Group radioGroup = new Group(this, SWT.SHADOW_ETCHED_IN);
		radioGroup.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
	    radioGroup.setLayout(new RowLayout());
		Button smallButton = new Button(radioGroup, SWT.RADIO);
		smallButton.setText(ViewSize.SMALL.getLabel());
		smallButton.setSelection(false);
		Button mediumButton = new Button(radioGroup, SWT.RADIO);
		mediumButton.setText(ViewSize.MEDIUM.getLabel());
		mediumButton.setSelection(true);
		Button largeButton = new Button(radioGroup, SWT.RADIO);
		largeButton.setText(ViewSize.LARGE.getLabel());
		largeButton.setSelection(false);

		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
	    canvasHolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tilePickerCanvas = new MyTilePickerCanvas(canvasHolder);
		tilePickerCanvas.tileImage = tileSet.getTilesImage(ViewSize.MEDIUM);
		canvasHolder.setContent(tilePickerCanvas);
		canvasHolder.setExpandHorizontal(true);
		canvasHolder.setExpandVertical(true);
		Rectangle rect = tilePickerCanvas.tileImage.getBounds();
		canvasHolder.setMinSize(rect.width, rect.height);
		
		// label
		tileLabel = new Label(this, SWT.CENTER);
		tileLabel.setText(Constants.NO_SELECTION_LABEL);
		tileLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// ** radio button listeners **
		smallButton.addListener(SWT.Selection,
				new ViewSizeListener(ViewSize.SMALL, smallButton));
		mediumButton.addListener(SWT.Selection,
				new ViewSizeListener(ViewSize.MEDIUM, mediumButton));
		largeButton.addListener(SWT.Selection,
				new ViewSizeListener(ViewSize.LARGE, largeButton));		
	}
	
	public void setTileSelection(TileSelection tileSelection) {
		this.tileSelection = tileSelection;
	}
	
	private class MyTilePickerCanvas extends TilePickerCanvas {
		
		public MyTilePickerCanvas(Composite parent) {
			super(parent);
		}
				
		@Override
		public boolean isSelectionValid(Point tilePoint) {
			if (tileSet.getTile(tilePoint) == null) {
				return false;
			}
			return true;
		}

		@Override
		public void tileSelectedAction() {
			tileSelection.tileSelected(tileSet.getTile(selectedTile));
		}

		@Override
		public void setLabelText() {
			if (highlightTile.equals(NO_SELECTION)) {
				tileLabel.setText(Constants.NO_SELECTION_LABEL);
			}
			else {
				Tile tile = tileSet.getTile(highlightTile);
				if (tile == null) {
					tileLabel.setText(Constants.NO_SELECTION_LABEL);					
				}
				else {
					tileLabel.setText(highlightTile.x + Constants.LABEL_COMMA + 
							highlightTile.y + Constants.SEPARATOR + tile.getName());					
				}
			}
		}
	}
	
	private class ViewSizeListener implements Listener {

		private ViewSize myViewSize;
		private Button myRadioButton;
		
		public ViewSizeListener(ViewSize viewSize, Button radioButton) {
			myViewSize = viewSize;
			myRadioButton = radioButton;
		}

		public void handleEvent(Event event) {
			if (myRadioButton.getSelection()) {
				tilePickerCanvas.viewSize = myViewSize;
				tilePickerCanvas.tileImage = tileSet.getTilesImage(myViewSize);
				Rectangle rect = tilePickerCanvas.tileImage.getBounds();
				canvasHolder.setMinSize(rect.width, rect.height);
				tilePickerCanvas.redraw();
			}
		}
	}
	
	@Override
	public void dispose() {
		super.dispose();
		tileSet.dispose();
	}
	
	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) throws Exception {
		
		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		shell.setLayout(new GridLayout());
		
		TileSet tileSet = TileSet.loadTileSet();
		TilePicker tilePicker = new TilePicker(shell, tileSet);
		tilePicker.setTileSelection(TileSelectionStub.getInstance());
					
		shell.setSize(800, 400);
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		// dispose resources
		tilePicker.dispose();
		ImageHelper.dispose();
		display.dispose();
	}
}
