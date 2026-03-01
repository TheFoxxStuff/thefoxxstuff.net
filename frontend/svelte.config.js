import adapter from '@sveltejs/adapter-static';

export default {
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: 'index.html',
			precompress: true,
			strict: true
		})
	},
	compilerOptions: {
		// Suppress non-critical a11y warnings that are handled at runtime
	},
	onwarn: (warning, handler) => {
		// Ignore autofocus warning (intentional UX choice)
		if (warning.code === 'a11y_autofocus') return;
		handler(warning);
	}
};
