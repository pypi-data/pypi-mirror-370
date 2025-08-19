import { INotebookTracker } from '@jupyterlab/notebook';
const SQL_MIME = 'text/x-isql';
const ISQLDisplayName = 'ISQL';
const hasDropdown = (cell) => !!cell.node.querySelector('.cell-kernel-selector-wrapper');
const isISQLKernel = (panel) => {
    var _a;
    return ((_a = panel.sessionContext.kernelDisplayName) !== null && _a !== void 0 ? _a : '').toLowerCase() ===
        ISQLDisplayName.toLowerCase();
};
const extension = {
    id: 'cell-kernel-selector',
    autoStart: true,
    requires: [INotebookTracker],
    activate: (_app, tracker) => {
        console.log('Inline Kernel Selector Activated');
        (() => {
            if (document.getElementById('sql-python-cell-switch‑css'))
                return;
            const font = Object.assign(document.createElement('link'), {
                rel: 'stylesheet',
                href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap'
            });
            const style = Object.assign(document.createElement('style'), {
                id: 'sql-python-cell-switch‑css',
                textContent: /* css */ `
          select.cell-kernel-selector-dropdown option[value="Python"]{
            color:rgb(37,235,37);font-weight:600;
          }
          select.cell-kernel-selector-dropdown option[value="SQL"]{
            color:rgb(21,17,224);font-weight:600;
          }
          .jp-InputArea-editor.has-kernel-dropdown{
            position:relative!important;padding-top:32px!important;
          }
          .cell-kernel-selector-wrapper{
            position:absolute;top:6px;left:8px;z-index:20;
            background:var(--jp-layout-color2);
            border:1px solid var(--jp-border-color2);
            padding:2px 6px;border-radius:4px;
            display:flex;gap:4px;font:500 11px 'Inter',sans-serif;
          }
          select.cell-kernel-selector-dropdown{
            padding:2px 6px;font:11px 'Inter',sans-serif;
            border:1px solid var(--jp-border-color2);
            background:var(--jp-layout-color0);max-width:120px;cursor:pointer;
          }
        `
            });
            document.head.append(font, style);
        })();
        const choices = ['-- Select Kernel --', 'Python', 'SQL'];
        const pythonHdr = "#Code in Python below. Don't Remove this Header!!";
        const addDropdown = (cell) => {
            if (hasDropdown(cell))
                return;
            const host = cell.node.querySelector('.jp-InputArea-editor');
            if (!host)
                return;
            const sel = document.createElement('select');
            sel.className = 'cell-kernel-selector-dropdown';
            choices.forEach(n => {
                const opt = document.createElement('option');
                opt.text = n;
                opt.value = n === '-- Select Kernel --' ? '' : n;
                sel.appendChild(opt);
            });
            let prog = false;
            const apply = (k) => {
                var _a;
                const srcLines = cell.model.sharedModel.source
                    .split('\n')
                    .filter(l => !l.trim().startsWith('#Kernel:') && l !== pythonHdr);
                const newLines = k === 'Python'
                    ? ['#Kernel: Python', pythonHdr, ...srcLines]
                    : [...srcLines];
                const newSrc = newLines.join('\n');
                if (newSrc === cell.model.sharedModel.source)
                    return;
                prog = true;
                cell.model.sharedModel.source = newSrc;
                cell.model.mimeType =
                    k === 'Python' ? 'text/x-python' : SQL_MIME;
                prog = false;
                (_a = cell.editor) === null || _a === void 0 ? void 0 : _a.setCursorPosition({
                    line: k === 'Python' ? 2 : 0,
                    column: 0
                });
            };
            const sync = () => {
                var _a;
                if (prog)
                    return;
                const first = (_a = cell.model.sharedModel.source.split('\n')[0]) === null || _a === void 0 ? void 0 : _a.toLowerCase();
                sel.value = first === '#kernel: python' ? 'Python' : 'SQL';
            };
            sel.onchange = () => apply((sel.value || 'SQL'));
            cell.model.contentChanged.connect(sync);
            const wrap = document.createElement('div');
            wrap.className = 'cell-kernel-selector-wrapper';
            wrap.innerHTML = '<label>Run:</label>';
            wrap.appendChild(sel);
            host.appendChild(wrap);
            host.classList.add('has-kernel-dropdown');
            sync();
        };
        const inject = (panel) => panel.content.widgets.forEach(w => {
            if (w.model.type === 'code')
                addDropdown(w);
        });
        const removeAll = (panel) => panel.content.widgets.forEach(w => {
            var _a, _b;
            if (w.model.type !== 'code')
                return;
            (_a = w.node
                .querySelector('.cell-kernel-selector-wrapper')) === null || _a === void 0 ? void 0 : _a.remove();
            (_b = w.node
                .querySelector('.jp-InputArea-editor')) === null || _b === void 0 ? void 0 : _b.classList.remove('has-kernel-dropdown');
        });
        tracker.widgetAdded.connect((_t, panel) => {
            var _a;
            const refresh = () => {
                if (isISQLKernel(panel)) {
                    inject(panel);
                }
                else {
                    removeAll(panel);
                }
            };
            panel.context.ready.then(refresh);
            panel.sessionContext.kernelChanged.connect(refresh);
            (_a = panel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect((_list, ch) => {
                var _a;
                if (!isISQLKernel(panel))
                    return;
                (_a = ch.newValues) === null || _a === void 0 ? void 0 : _a.forEach(m => {
                    if (m.type !== 'code')
                        return;
                    const v = panel.content.widgets.find((w) => w.model === m);
                    v === null || v === void 0 ? void 0 : v.ready.then(() => requestAnimationFrame(() => addDropdown(v)));
                });
            });
            panel.content.activeCellChanged.connect(() => {
                if (!isISQLKernel(panel))
                    return;
                const c = panel.content.activeCell;
                if ((c === null || c === void 0 ? void 0 : c.model.type) === 'code')
                    addDropdown(c);
            });
        });
    }
};
export default extension;
