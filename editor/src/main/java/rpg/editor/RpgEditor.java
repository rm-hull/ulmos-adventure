package rpg.editor;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.MenuAdapter;
import org.eclipse.swt.events.MenuEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.components.MapEditor;
import rpg.editor.components.RecentTiles;
import rpg.editor.components.TilePicker;
import rpg.editor.core.DisplayHelper;
import rpg.editor.core.WarningDialog;
import rpg.editor.model.RpgMap;
import rpg.editor.model.TileSet;

public class RpgEditor {
	
	private static final RGB TAB_COLOUR = new RGB(142, 175, 230);
	
	private Display display = DisplayHelper.getDisplay();
	private Shell shell = DisplayHelper.getShell();
	
	private CTabFolder folder;
	
	private MapEditor mapEditor; 
	
	private RecentTiles recentTiles;
	
	private RpgEditor() {
		shell.setLayout(new GridLayout());
		shell.setText("RPG Editor");

		Menu menuBar = new Menu(shell, SWT.BAR);
		shell.setMenuBar(menuBar);
		MenuItem menuItem = new MenuItem(menuBar, SWT.CASCADE);
		menuItem.setText("File");
		Menu fileMenu = new Menu(shell, SWT.DROP_DOWN);
		menuItem.setMenu(fileMenu);
		addOpenTileset(fileMenu);
		new MenuItem(fileMenu, SWT.SEPARATOR);
		addNewMap(fileMenu);
		addOpenMap(fileMenu);
		final MenuItem saveMap = addSaveMap(fileMenu);
		final MenuItem saveMapAs = addSaveMapAs(fileMenu);
		fileMenu.addMenuListener(new MenuAdapter() {
			@Override
			public void menuShown(MenuEvent e) {
				if (mapEditor.getMap() == null) {
					saveMap.setEnabled(false);
					saveMapAs.setEnabled(false);
				}
				else {
					saveMap.setEnabled(true);
					saveMapAs.setEnabled(true);					
				}
			}
		});

		
		Menu popupMenu = new Menu(shell, SWT.POP_UP);
		addOpenTileset(popupMenu);

		// Create a SashForm to hold the other widgets
		SashForm hForm = new SashForm(shell, SWT.HORIZONTAL | SWT.SMOOTH);
		hForm.setLayoutData(new GridData (SWT.FILL, SWT.FILL, true, true));
		hForm.setSashWidth(5);

		SashForm vForm = new SashForm(hForm, SWT.VERTICAL | SWT.SMOOTH);
		vForm.setLayoutData(new GridData (SWT.FILL, SWT.FILL, true, true));
		vForm.setSashWidth(5);
		
		folder = new CTabFolder(vForm, SWT.BORDER | SWT.RESIZE);
		folder.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		folder.setSimple(false);
		folder.setSelectionBackground(new Color(display, TAB_COLOUR));
		folder.setMenu(popupMenu);

		recentTiles = new RecentTiles(vForm, SWT.BORDER);
		recentTiles.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		vForm.setWeights(new int[] {4, 1});

		mapEditor = new MapEditor(hForm, SWT.BORDER);

		hForm.setWeights(new int[] {4, 6});
	}
	
	public void run(int width, int height) {
		shell.setSize(width, height);
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		display.dispose();		
	}
	
	private MenuItem addOpenTileset(Menu menu) {
		MenuItem openTileSet = new MenuItem(menu, SWT.PUSH);
		openTileSet.setText("Open Tileset");
		openTileSet.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				// create new TilePicker
				TileSet tileSet = TileSet.loadTileSet();
				if (tileSet != null) {
					TilePicker tilePicker = new TilePicker(folder, tileSet);
					tilePicker.setTileSelection(recentTiles);
					CTabItem item = new CTabItem(folder, SWT.CLOSE);
					item.setText(tileSet.getName());
					item.setControl(tilePicker);
					folder.setSelection(item);					
				}
			}
		});
		return openTileSet;
	}

	private MenuItem addNewMap(Menu menu) {
		MenuItem newMap = new MenuItem(menu, SWT.PUSH);
		newMap.setText("New Map");
		newMap.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				// create new map and add it to the map editor
				RpgMap rpgMap = null;
				if (mapEditor.getMap() == null) {
					rpgMap = RpgMap.newRpgMap();
				}
				else {
					WarningDialog warningDialog = new WarningDialog(shell);
					if (warningDialog.getResponse("This will replace the current map!")) {
						rpgMap = RpgMap.newRpgMap();
					}
				}
				if (rpgMap != null) {
					mapEditor.setMap(rpgMap);						
				}
			}
		});
		return newMap;
	}
	
	private MenuItem addOpenMap(Menu menu) {
		MenuItem openMap = new MenuItem(menu, SWT.PUSH);
		openMap.setText("Open Map");
		openMap.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				// load map and add it to the map editor
				RpgMap rpgMap = null;
				if (mapEditor.getMap() == null) {
					rpgMap = RpgMap.loadRpgMap();
				}
				else {
					WarningDialog warningDialog = new WarningDialog(shell);
					if (warningDialog.getResponse("This will replace the current map!")) {
						rpgMap = RpgMap.loadRpgMap();
					}
				}
				if (rpgMap != null) {
					mapEditor.setMap(rpgMap);						
				}
			}
		});
		return openMap;
	}

	private MenuItem addSaveMap(Menu menu) {
		MenuItem saveMap = new MenuItem(menu, SWT.PUSH);
		saveMap.setText("Save Map");
		saveMap.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				RpgMap map = mapEditor.getMap();
				if (map != null) {
					map.saveRpgMap();
				}
			}
		});
		return saveMap;
	}

	private MenuItem addSaveMapAs(Menu menu) {
		MenuItem saveMapAs = new MenuItem(menu, SWT.PUSH);
		saveMapAs.setText("Save Map As");
		saveMapAs.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				RpgMap map = mapEditor.getMap();
				if (map != null) {
					map.saveRpgMap(true);
				}
			}
		});
		return saveMapAs;
	}

	public static void main(String[] args) {
		RpgEditor editorApp = new RpgEditor();
		editorApp.run(1000, 600);
	}
}
