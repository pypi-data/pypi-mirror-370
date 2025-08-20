"use strict";
(self["webpackChunkm269_25j_student"] = self["webpackChunkm269_25j_student"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Initialization data for the m269-25j-student extension.
 */
const colourise_command = 'm269-25j-student:colourise';
const plugin = {
    id: 'm269-25j-student:plugin',
    description: 'An extension for OU Students studying M269 in 25J',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette],
    activate: (app, palette) => {
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
            execute: async (args) => {
                console.log('Command called');
                const currentWidget = app.shell.currentWidget;
                if (currentWidget &&
                    'content' in currentWidget &&
                    currentWidget['content'] instanceof _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.Notebook) {
                    console.log('Constructore say NotebookPanel');
                    const notebookPanel = currentWidget;
                    const notebook = notebookPanel.content;
                    console.log('Colourising cells');
                    for (let i = 0; i < notebook.widgets.length; i++) {
                        console.log(i);
                        const currentCell = notebook.widgets[i];
                        const meta = currentCell.model.metadata;
                        const celltype = meta['CELLTYPE'];
                        console.log(celltype);
                        if (celltype === 'ANSWER') {
                            currentCell.addClass('m269-answer');
                        }
                        else if (celltype === "FEEDBACK") {
                            currentCell.addClass('m269-feedback');
                        }
                        else if (celltype === "MARKCODE") {
                            currentCell.addClass('m269-feedback');
                        }
                        else if (celltype === "SOLUTION" || celltype === "SECREF" || celltype === "GRADING") {
                            currentCell.addClass('m269-tutor');
                        }
                    }
                }
                else {
                    console.log('Constructor say no potatoes');
                    if (currentWidget) {
                        console.log(currentWidget.constructor.name);
                    }
                    else {
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.c00786e068d12dfb3095.js.map