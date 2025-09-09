# Fix Import Functionality

## Issues Identified

1. **JavaScript Syntax Error**: Fixed broken comment in dashboard.js
2. **Function Not Found**: Browser cache or server restart needed
3. **Missing Modal Elements**: Need to verify HTML structure

## Solutions

### 1. Clear Browser Cache
The browser may be caching the old JavaScript file. To fix:

**Option A: Hard Refresh**
- Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
- Or open Developer Tools (F12) and right-click refresh button → "Empty Cache and Hard Reload"

**Option B: Disable Cache in DevTools**
- Open Developer Tools (F12)
- Go to Network tab
- Check "Disable cache" checkbox
- Refresh the page

### 2. Restart Dashboard Server
The server may need to be restarted to pick up JavaScript changes:

```bash
# Stop current server (Ctrl+C)
python launch_dashboard.py
```

### 3. Verify JavaScript Loading
Open browser Developer Tools (F12) and check:

**Console Tab:**
- Look for any JavaScript errors
- Should see no "Unexpected identifier" errors

**Network Tab:**
- Verify `dashboard.js` loads successfully (status 200)
- Check file size is reasonable (should be ~50KB+)

**Sources Tab:**
- Navigate to `static/js/dashboard.js`
- Search for `showImportModal` function
- Verify it exists and is properly formatted

### 4. Test Import Functionality

**Step 1: Basic Test**
1. Open http://localhost:9000
2. Open Developer Tools Console (F12)
3. Type: `typeof showImportModal`
4. Should return: `"function"`

**Step 2: Function Test**
1. In console, type: `showImportModal()`
2. Should open the import modal

**Step 3: UI Test**
1. Click "Import Data" button in dashboard
2. Should open import modal without errors

### 5. Alternative: Direct File Test
If issues persist, test the JavaScript file directly:

1. Open: `test_dashboard_js.html` in browser
2. Should show function test results
3. Verify import modal opens

### 6. Manual Fix (if needed)
If the function is still missing, add it manually:

```javascript
// Add to browser console temporarily
function showImportModal() {
    const modal = new bootstrap.Modal(document.getElementById('importDataModal'));
    modal.show();
}
```

## Verification Steps

1. **Check Function Exists:**
   ```javascript
   console.log(typeof showImportModal); // Should be "function"
   ```

2. **Test Modal Opening:**
   ```javascript
   showImportModal(); // Should open modal
   ```

3. **Check Modal Element:**
   ```javascript
   console.log(document.getElementById('importDataModal')); // Should not be null
   ```

4. **Test Import Endpoints:**
   ```bash
   python test_import_endpoints.py
   ```

## Expected Results

After fixing:
- ✅ No JavaScript console errors
- ✅ "Import Data" button works
- ✅ Import modal opens properly
- ✅ File selection and validation work
- ✅ Import process completes successfully

## Troubleshooting

**If function still not found:**
1. Check if dashboard.js is loading: Network tab in DevTools
2. Verify file content: Sources tab in DevTools
3. Look for syntax errors: Console tab in DevTools

**If modal doesn't open:**
1. Check if Bootstrap is loaded: `typeof bootstrap` should be "object"
2. Verify modal HTML exists: `document.getElementById('importDataModal')`
3. Check for CSS/Bootstrap conflicts

**If import fails:**
1. Check API endpoints: `python test_import_endpoints.py`
2. Verify server is running: http://localhost:9000/api/expert-review/dashboard/overview
3. Check network requests in DevTools

## Files Modified

- ✅ `backend/api/expert_review_api.py` - Import endpoints added
- ✅ `frontend/templates/dashboard.html` - Import modal added
- ✅ `frontend/static/js/dashboard.js` - Import functions added (syntax fixed)
- ✅ `sample_import_data.json` - Test data created

## Next Steps

1. Clear browser cache and restart server
2. Test import functionality
3. If working, proceed with actual data import
4. If not working, use debug files to identify specific issues