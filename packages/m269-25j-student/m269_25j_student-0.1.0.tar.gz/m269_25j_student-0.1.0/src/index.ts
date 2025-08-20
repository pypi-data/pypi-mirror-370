import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import type { NotebookPanel } from '@jupyterlab/notebook';
import { Notebook } from '@jupyterlab/notebook';
/**
 * Initialization data for the m269-25j-student extension.
 */
const colourise_command = 'm269-25j-student:colourise';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'm269-25j-student:plugin',
  description: 'An extension for OU Students studying M269 in 25J',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension m269-25j-student is activated!');
    // Inject custom styles
    const style = document.createElement('style');
    style.textContent = `
      .m269-answer {
        background-color:rgb(255, 255, 204) !important;
      }
      .m269-feedback {
        background-color:rgb(93, 163, 243) !important;
      }
      .m269-tutor {
        background-color: rgb(249, 142, 142) !important;
      }
    `;
    document.head.appendChild(style);
    // Colourise command
    app.commands.addCommand(colourise_command, {
      label: 'M269 Colourise',
      caption: 'M269 Colourise',
      execute: async (args: any) => {
        console.log('Command called');
        const currentWidget = app.shell.currentWidget; 
        if ( currentWidget &&
            'content' in currentWidget &&
            currentWidget['content'] instanceof Notebook
          ) {
          console.log('Constructore say NotebookPanel');
          const notebookPanel = currentWidget as NotebookPanel;
          const notebook = notebookPanel.content;
          console.log('Colourising cells');
          for (let i = 0; i < notebook.widgets.length; i++) {
            console.log(i);
            const currentCell = notebook.widgets[i];
            const meta = currentCell.model.metadata as any;
            const celltype = meta['CELLTYPE'];
            console.log(celltype);
            if (celltype === 'ANSWER') {
              currentCell.addClass('m269-answer');
            } else if (celltype === "FEEDBACK") {
              currentCell.addClass('m269-feedback');
            } else if (celltype === "MARKCODE") {
              currentCell.addClass('m269-feedback');              
            } else if (celltype === "SOLUTION" || celltype === "SECREF" || celltype === "GRADING") {
              currentCell.addClass('m269-tutor');
            }
          }
        } else {
          console.log('Constructor say no potatoes');
          if (currentWidget) {
            console.log(currentWidget.constructor.name);
          } else {
            console.log('No current widget!');
          }
        }
      }
    });
    // End colourise command
    const category = 'M269-25j';
    palette.addItem({ command: colourise_command, category, args: { origin: 'from palette' } });
  }
};

export default plugin;
