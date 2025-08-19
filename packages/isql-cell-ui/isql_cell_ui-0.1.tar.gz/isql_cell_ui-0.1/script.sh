# 1. Compile & stage the extension
npm install
npm run build:labext

# # 2. Create the .tgz archive
mkdir -p resources
npm pack ./labextension --pack-destination resources

# 3. Confirm output
# ls resources/
# → cell-kernel-selector-0.x.0.tgz

# 4. Package the wheel
python3 -m build
