(async () => {
    try {
        const mod = await import('fs://game/<REL_PATH>');

        // Transcrypt usually exports { <MOD> } or default, or direct names
        // const ns = mod.test || mod.default || mod;
        // optional: expose for non-module code
        // window.<MOD> = ns;
    } catch (e) {
        console.error('Failed to import <MOD>', e);
    }
})();
