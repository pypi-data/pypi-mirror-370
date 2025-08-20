const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

app.use(bodyParser.json());
const loadedModules = {};

// 动态获取当前脚本的路径
const currentScriptPath = process.argv[1];

function loadScripts(directory) {
    if (!fs.existsSync(directory)) {
        console.error(`Error: Directory not found: ${directory}`);
        return;
    }
    fs.readdirSync(directory).forEach(file => {
        const ext = path.extname(file);
        if (ext === '.js' || ext === '.jsx') {
            const moduleName = path.basename(file, ext);
            const scriptPath = path.join(directory, file);

            // 关键修正：跳过当前正在运行的脚本文件
            if (path.resolve(scriptPath) === path.resolve(currentScriptPath)) {
                console.log(`Skipping server file: ${file}`);
                return;
            }

            try {
                const scriptCode = fs.readFileSync(scriptPath, 'utf-8');
                const module = { exports: {} };
                // 模拟 CommonJS 模块系统
                const wrappedCode = `(function(exports, require, module) {
                    ${scriptCode}
                })(module.exports, require, module);`;

                eval(wrappedCode);
                loadedModules[moduleName] = module.exports;



                console.log(`Loaded module: ${moduleName}`);
            } catch (e) {
                console.error(`Error loading script ${file}: ${e.message}`);
            }
        }

    });

}

const scriptsDir = process.argv[2] ? path.resolve(process.argv[2]) : path.resolve(process.cwd(), './resources/js');
const port = process.argv[3] ? parseInt(process.argv[3]) : (process.env.PORT || 3000);
loadScripts(scriptsDir);


app.post('/:filename/invoke', async (req, res) => {
    try {
        const { filename } = req.params;
        const { func_name, args = [] } = req.body;
        console.log(`${req.path} was accessed.`)
        if (!loadedModules[filename]) {
            return res.status(404).json({ success: false, error: `Module '${filename}' not found.` });
        }

        const module = loadedModules[filename];
        if (typeof module[func_name] === 'function') {
            const result = await module[func_name](...args);
            res.json({ success: true, result });
        } else {
            res.status(404).json({ success: false, error: `Function '${func_name}' not found in module '${filename}'.` });
        }
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/status', (req, res) => {
    res.json({ status: 'running', service_name: 'js_invoker_microservice' });
});

const os = require('os');


app.listen(port, '0.0.0.0', () => {
    const listenAddress = '0.0.0.0';
    console.log(`Namespaced invoker service is running on http://${listenAddress}:${port}`);
    console.log(`Scanning directory: ${scriptsDir}`);
    if (listenAddress === '0.0.0.0') {
        const networkInterfaces = os.networkInterfaces();
        const localIps = new Set();

        localIps.add('127.0.0.1');

        for (const interfaceName in networkInterfaces) {
            const ifaces = networkInterfaces[interfaceName];
            for (const iface of ifaces) {
                if (iface.family === 'IPv4' && !iface.internal) {
                    if (iface.address.startsWith('192.168.')) {
                        localIps.add(iface.address);
                    }
                }
            }
        }
        console.log("scanned result:")
        console.log(loadedModules)
        console.log("If the result is missing, please check whether the module has the same name and whether there are exports before the method.")
        const sortedLocalIps = Array.from(localIps).sort();

        console.log('--- Local network address ---');
        sortedLocalIps.forEach(ip => {
            console.log(`  - http://${ip}:${port}`);
        });
        console.log('-----------------------------');
    }
});
