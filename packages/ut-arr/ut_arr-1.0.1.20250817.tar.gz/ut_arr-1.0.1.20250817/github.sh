# create a new repository on the command line
git init

# stage all changes
git add .

# commit changes
git commit -m "first commit"
git commit -m "second commit"
git commit -m "third commit"

git branch -M main

git config --global --add safe.directory /mnt/hgfs/SOURCE/python/ut_arr
git config --global user.email "bernd.stroehle@gmail.com"
git config --global user.name "Bernd Stroehle"

# push an existing repository from the command line
git remote add origin.ut_arr https://github.com/bs2910/ut_arr.git
git branch -M main
git push -u origin.ui_eviq_srr main

# Personal Access Classic Token
export PAC_TOKEN=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
curl -X PATCH \
-H "Authorization: token $PAC_TOKEN" \
-d '{"private": true}' \
https://api.github.com/repos/bs2910/ut_arr

gh login bs2910
gh repo create ap_cfg --public
gh repo create ap_mail --public
gh repo create ui_eviq_srr --private
gh repo create ui_eviq_wdp --private
gh repo create ut_aod --public
gh repo create ut_arr --public
gh repo create ut_com --public
gh repo create ut_ctl --public
gh repo create ut_dfr --public
gh repo create ut_dic --public
gh repo create ut_eviq --public
gh repo create ut_flt --public
gh repo create ut_ioc --public
gh repo create ut_log --public
gh repo create ut_obj --public
gh repo create ut_pac --public
gh repo create ut_path --public
gh repo create ut_prc --public
gh repo create ut_wdp --public
gh repo create ut_xls --public
