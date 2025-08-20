from abstract_paths.content_utils.src.find_content import findContentAndEdit
diff = """-interface Props {
-  setInfodata?: any; // optional
-  setLoading?: any;
-};
+interface Props {
+  setInfoData?: (v: any) => void; // canonical
+  setLoading?: (v: boolean) => void;
+}

 ...
-  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
+  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
     e.preventDefault();
-    const { setInfodata, setLoading } = props; // Destructure for safety
+    const { setInfoData, setLoading } = props;
     setLocalLoading(true);
     alertit(urlInput)
     try {
       await VideoSubmit({
         e,
         urlInput,
         setLoading: setLoading || setLocalLoading,
-        setInfodata, // Pass directly
+        setInfoData, // ✅ correct name
         setResponse: (msg: string) => console.log(msg)
       });
"""
def get_sub_add(diffs):
    diffs.append({"sub":[],"add":[]})
    return diffs
diffs = []
endiff = True
all_difs = []
def elimComments(string):
    if '//' in string:
        for i in range(len(string)):
            if str(string[-i])+str(string[-i+1]) == '//':
                return eatOuter(string[:-i],' ')
                
    return string
for dif in diff.split('\n'):
    
    if dif.startswith('-'):
        if endiff:
            diffs = get_sub_add(diffs)
            endiff=False
        diffs[-1]["sub"].append(dif[1:])
        
    elif dif.startswith('+'):
        diffs[-1]["add"].append(dif[1:])
    else:
        if endiff==False:
            content = findContentAndEdit(
                directory='/var/www/html/clownworld/bolshevid',
                exclude_dirs='node_modules',
                strings=all_difs,
                total_strings=True,
                parse_lines=False,
                spec_line=False,
                get_lines=True,
                edit_lines=False
            )
            print(all_difs)
            input(content) 
            endiff = True


  
content = findContent(
        directory='/var/www html/clownworld/bolshevid',
        exclude_dirs='node_modules',
        strings=all_difs,
        total_strings=True,
        parse_lines=True,
        spec_line=False,
        get_lines=True
    )
input(content)
