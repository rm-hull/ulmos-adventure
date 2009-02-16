package rpg.editor.components;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Dialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;

import rpg.editor.Constants;

public class WarningDialog extends Dialog {
	
	private boolean response = false;
	
	public WarningDialog(Shell parent, int style) {
		super(parent, style);
	}
	
	public WarningDialog(Shell parent) {
		this(parent, SWT.NONE);
	}
	
	public boolean getResponse(String warning) {
		Shell parent = getParent();
		final Shell shell = new Shell(parent, SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL);
		shell.setText("Warning");
		GridLayout gridLayout = new GridLayout();
		gridLayout.verticalSpacing = 12;
		gridLayout.marginWidth = 20;
		gridLayout.marginTop = 12;
		shell.setLayout(gridLayout);
		
		// messages
		if (warning != null) {
			Label label = new Label(shell, SWT.CENTER);
			label.setText(warning);
			label.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		}
		
		// ok + cancel buttons
		Composite buttonBar = new Composite(shell, SWT.NONE);
		buttonBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false));
		buttonBar.setLayout(new RowLayout());
		Button ok = new Button(buttonBar, SWT.PUSH);
		ok.setText(Constants.OK);
		ok.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				response = true;
				shell.dispose();
			}
		});
		Button cancel = new Button(buttonBar, SWT.PUSH);
		cancel.setText(Constants.CANCEL);
		cancel.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				shell.dispose();
			}
		});
		
		// center the dialog
		shell.pack();		
		Rectangle parentBounds = parent.getBounds();
		Rectangle childBounds = shell.getBounds();
		int x = parentBounds.x + (parentBounds.width - childBounds.width) / 2;
		int y = parentBounds.y + (parentBounds.height - childBounds.height) / 2;
		shell.setLocation(x, y);
		
		// and display
		shell.open();
		Display display = parent.getDisplay();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) display.sleep();
		}
		
		return response;
	}
}
