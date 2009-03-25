package rpg.editor.components;

import java.util.HashSet;
import java.util.Set;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.events.MenuAdapter;
import org.eclipse.swt.events.MenuEvent;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseMoveListener;
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
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.Constants;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.ImageHelper;
import rpg.editor.core.SharedTileSelection;
import rpg.editor.core.TileCanvas;
import rpg.editor.core.TileEditor;
import rpg.editor.core.TileEditorFactory;
import rpg.editor.core.TileImagesEditor;
import rpg.editor.core.TileLevelsEditor;
import rpg.editor.core.TileMasksEditor;
import rpg.editor.core.TileSelection;
import rpg.editor.core.TileSelectionStub;
import rpg.editor.model.MapTile;
import rpg.editor.model.RpgMap;
import rpg.editor.model.Tile;

/**
 * MapEditor is the main component in the application.  It allows users to add
 * selected tiles to a map and build up the map that will feature in the game.
 * This class also facilitates editing the information (eg. level data) required
 * by the game engine.
 * @author seldred
 */
public class MapEditor extends Composite {

    private TileSelection tileSelection = SharedTileSelection.getInstance();
	
    private ScrolledComposite canvasHolder;
    
    private MapEditorCanvas mapEditorCanvas;
    
    private Label tileLabel;
    
    private RpgMap map;

    private EditMode editMode = EditMode.ADD;

    public MapEditor(Composite parent) {
    	this(parent, SWT.NONE);
    }
    
	public MapEditor(Composite parent, int style) {
		
		super(parent, style);
		
		// layout setup
		setLayout(new GridLayout());
		setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
	    // radio buttons
	    Group radioGroup = new Group(this, SWT.SHADOW_ETCHED_IN);
		radioGroup.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
	    radioGroup.setLayout(new RowLayout());
	    Button addButton = new Button(radioGroup, SWT.RADIO);
	    addButton.setText("Add");
	    addButton.setSelection(true);
	    Button insertButton = new Button(radioGroup, SWT.RADIO);
	    insertButton.setText("Insert");
	    insertButton.setSelection(false);
	    Button noneButton = new Button(radioGroup, SWT.RADIO);
	    noneButton.setText("None");
	    noneButton.setSelection(false);
		
		// canvas
	    canvasHolder = new ScrolledComposite(this, SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER);
	    canvasHolder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		mapEditorCanvas = new MapEditorCanvas(canvasHolder);
		canvasHolder.setContent(mapEditorCanvas);
		canvasHolder.setExpandHorizontal(true);
		canvasHolder.setExpandVertical(true);

		// label
		tileLabel = new Label(this, SWT.CENTER);
		tileLabel.setText(Constants.NO_SELECTION_LABEL);
		tileLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		addButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				editMode = EditMode.ADD;
			}
		});
		insertButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				editMode = EditMode.INSERT;
			}
		});
		noneButton.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				editMode = EditMode.NONE;
			}
		});
	}
	
	private class MapEditorCanvas extends TileCanvas {

		private static final String SEND_TO_BACK = "Send To Back";
		private static final String EDIT_IMAGES = "Edit Images";
		private static final String EDIT_LEVELS = "Edit Levels";
		private static final String EDIT_MASKS = "Edit Masks";
		private static final String KEEP_TOP = "Keep Top";
		private static final String CLEAR = "Clear";
		
		// private static final String CUT = "Cut";
		// private static final String COPY = "Copy";
		// private static final String PASTE = "Paste";
		
		public MapEditorCanvas(Composite parent) {
			super(parent);

			final Menu popupMenu = new Menu(this);
			populatePopupMenu(popupMenu);
			setMenu(popupMenu);
			popupMenu.addMenuListener(new MenuAdapter() {
				@Override
				public void menuShown(MenuEvent e) {
					Set<String> toEnable = new HashSet<String>();
					if (highlightTile != null) {
						MapTile mapTile = map.getMapTile(highlightTile);
						int tileDepth = mapTile.getTileDepth();
						if (tileDepth > 0) {
							toEnable.add(CLEAR);
							toEnable.add(EDIT_IMAGES);
							toEnable.add(EDIT_LEVELS);
							toEnable.add(EDIT_MASKS);
							if (tileDepth > 1) {
								toEnable.add(SEND_TO_BACK);
								toEnable.add(KEEP_TOP);
							}
						}
					}
					enableMenuItems(popupMenu, toEnable);
				}
			});
			
			// ** mouse listener **
			addMouseListener(new MouseAdapter() {
				@Override
				public void mouseDown(MouseEvent e) {
					// try {
					if (highlightTile != null) {
						if (e.button == 1) {
							if (tileSelection.isTileSelected()) {
								Tile tile = tileSelection.getSelectedTile();
								if (editMode == EditMode.ADD) {
									map.addTile(highlightTile, tile);
								}
								else if (editMode == EditMode.INSERT) {
									map.insertTile(highlightTile, tile);
								}
								redraw();
								setLabelText();
							}
						}					
					}
					/*} catch (Exception ex) {
						ex.printStackTrace();
					}*/
				}
			});

			// ** mouse move listener **
			addMouseMoveListener(new MouseMoveListener() {
				public void mouseMove(MouseEvent e) {
					if (tileImage != null) {
						Point previousHighlightTile = highlightTile;
						highlightTile = determineTilePoint(e);
						if ((highlightTile != null) && (!highlightTile.equals(previousHighlightTile))) {
							redraw();
							setLabelText();
						}					
					}
				}
			});
		}
		
		public void setLabelText() {
			if (highlightTile == null) {
				tileLabel.setText(Constants.NO_SELECTION_LABEL);
			}
			else {
				MapTile mapTile = map.getMapTile(highlightTile);				
				tileLabel.setText(highlightTile.x + Constants.LABEL_COMMA +
						highlightTile.y + Constants.SEPARATOR + mapTile.getLabel());
			}
		}
		
		private void populatePopupMenu(Menu menu) {
			// dynamic options
			MenuItem sendToBack = new MenuItem(menu, SWT.PUSH);
			sendToBack.setText(SEND_TO_BACK);
			sendToBack.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					map.sendToBack(highlightTile);
					redraw();
				}
			});
			MenuItem keepTop = new MenuItem(menu, SWT.PUSH);
			keepTop.setText(KEEP_TOP);
			keepTop.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					map.keepTop(highlightTile);
					redraw();
					setLabelText();
				}
			});
			MenuItem clear = new MenuItem(menu, SWT.PUSH);
			clear.setText(CLEAR);
			clear.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					map.clear(highlightTile);
					redraw();
					setLabelText();
				}
			});
			
			// separator
			new MenuItem(menu, SWT.SEPARATOR);
			
			// edit options
			MenuItem editImages = new MenuItem(menu, SWT.PUSH);
			editImages.setText(EDIT_IMAGES);
			editImages.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					MapTile mapTile = map.getMapTile(highlightTile);
					TileEditorFactory editorFactory = new TileImagesEditorFactory();
					TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editorFactory);
					tileEditor.editTile(mapTile);
					setLabelText();
					// update map image
					map.updateTileImage(mapTile, highlightTile);
					redraw();
				}
			});
			MenuItem editLevels = new MenuItem(menu, SWT.PUSH);
			editLevels.setText(EDIT_LEVELS);
			editLevels.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					MapTile mapTile = map.getMapTile(highlightTile);
					TileEditorFactory editorFactory = new TileLevelsEditorFactory();
					TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editorFactory, 240, 320);
					tileEditor.editTile(mapTile);
					setLabelText();
				}
			});
			MenuItem editMasks = new MenuItem(menu, SWT.PUSH);
			editMasks.setText(EDIT_MASKS);
			editMasks.addListener(SWT.Selection, new Listener() {
				public void handleEvent(Event event) {
					MapTile mapTile = map.getMapTile(highlightTile);
					TileEditorFactory editorFactory = new TileMasksEditorFactory();
					TileEditDialog tileEditor = new TileEditDialog(DisplayHelper.getShell(), editorFactory);
					tileEditor.editTile(mapTile);
					setLabelText();
				}
			});
		}
				
		private void enableMenuItems(Menu menu, Set<String> toEnable) {
			for (MenuItem item: menu.getItems()) {
				if ((item.getStyle() == SWT.PUSH) && (toEnable.contains(item.getText()))) {
					item.setEnabled(true);
				}
				else {
					item.setEnabled(false);
				}
			}
		}
	}
	
	public void setMap(RpgMap map) {
		this.map = map;
		mapEditorCanvas.tileImage = map.getMapImage();
		Rectangle rect = map.getMapImage().getBounds();
		canvasHolder.setMinSize(rect.width, rect.height);
		mapEditorCanvas.redraw();
	}
	
	public RpgMap getMap() {
		return map;
	}
	
	/*@Override
	public void dispose() {
		super.dispose();
		// mapImage.dispose();
		for (int i = 0; i < mapTiles.length; i++) {
			for (int j = 0; j < mapTiles[i].length; j++) {
				mapTiles[i][j].dispose();
			}
		}
	}*/
	
	private enum EditMode {
		ADD, INSERT, NONE;
	}
	
	// =======================================
	// == inner class tile editor factories ==
	// =======================================
	
	public static class TileImagesEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileImagesEditor(myParent, mapTile);
		}
	}
	
	public static class TileLevelsEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileLevelsEditor(myParent, mapTile);
		}
	}
	
	public static class TileMasksEditorFactory implements TileEditorFactory {
		public TileEditor newTileEditor(Composite myParent, MapTile mapTile) {
			return new TileMasksEditor(myParent, mapTile);
		}
	}
	
	// =====================================================
	// == main method to test this component in isolation ==
	// =====================================================
	
	public static void main(String[] args) throws Exception {
		
		Display display = DisplayHelper.getDisplay();
		Shell shell = DisplayHelper.getShell();
		shell.setLayout(new GridLayout());
		
		MapEditor mapEditor = new MapEditor(shell);
		mapEditor.tileSelection = TileSelectionStub.getInstance();
		RpgMap rpgMap = RpgMap.newRpgMap();
		mapEditor.setMap(rpgMap);
		
		shell.setSize(600, 600);
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		// dispose resources
		mapEditor.dispose();
		ImageHelper.dispose();
		display.dispose();
	}
}
