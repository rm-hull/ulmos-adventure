package rpg.editor.core;

import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;

public class DisplayHelper {

	private static Display display;
	
	private static Shell shell;
	
	static {
		display = new Display();
		shell = new Shell(display);
	}

	public static Display getDisplay() {
		return display;
	}

	public static Shell getShell() {
		return shell;
	}
}
