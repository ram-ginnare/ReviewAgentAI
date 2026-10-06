# UI Changes

1. Added five mood faces directly below the 1–5 star rating controls:
   - 1 star: 😞
   - 2 stars: 😕
   - 3 stars: 😐
   - 4 stars: 🙂
   - 5 stars: 🤩
2. Changed the final "Start a new review" button from the secondary style to the primary button style so it matches the main action buttons.

Validation:
- Frontend TypeScript check (`npx tsc -b`) passed before packaging.
- Frontend Vitest/build could not run in the existing environment because the supplied node_modules was missing Rollup's Linux optional dependency. node_modules was removed from the ZIP; run `npm install` before local frontend testing.
