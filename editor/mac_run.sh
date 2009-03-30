SWT_JAR="$HOME/.m2/repository/org/eclipse/swt/carbon/macosx/3.4.0/macosx-3.4.0.jar"
java -cp $SWT_JAR:./target/editor-1.0.jar:./src/test/resources/ rpg.editor.RpgEditor -XstartOnFirstThread
