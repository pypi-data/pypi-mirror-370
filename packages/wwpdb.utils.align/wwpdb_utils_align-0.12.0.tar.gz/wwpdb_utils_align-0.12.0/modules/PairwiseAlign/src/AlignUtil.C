/*$$FILE$$*/
/*$$VERSION$$*/
/*$$DATE$$*/
/*$$LICENSE$*/
#include <stdio.h>
#include <stdlib.h>

#include "AlignUtil.h"

#ifndef MAX
#define MAX(X, Y)   (((X) > (Y))? (X): (Y))
#endif
#ifndef MIN
#define MIN(X, Y)   (((X) < (Y))? (X): (Y))
#endif

void AlignUtil::initAssignment(std::vector<std::vector<int> >& ss, const int& size)
{
       ss.clear();
       ss.reserve(size);

       std::vector<int> data;
       data.clear();
       data.push_back(0);
       for (int i = 0; i < size; ++i) {
            data[0] = i;
            ss.push_back(data);
       }
}

void AlignUtil::Alignment(std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb,
                          const double& gap_penalty, double (*sfunc)(const int&, const int&, void*), void* data)
{
       std::vector<SAVE> dr;
       dr.clear();
       int n = 60 * sb.size();
       dr.reserve(n);
       int origin = dynamic(sa, sb, gap_penalty, dr, sfunc, data);
       mu_trcback(origin, ss, sa, sb, dr);
}

void AlignUtil::Alignment(std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb,
                          const double& vv, const double& uu, double (*sfunc)(const int&, const int&, void*), void* data,
                          const std::vector<int>& linkage, const double& factor)
{
       std::vector<SAVE> dr;
       dr.clear();
       int n = 60 * sb.size();
       dr.reserve(n);
       int origin = dynamic(sa, sb, vv, uu, dr, sfunc, data, linkage, factor);
       mu_trcback(origin, ss, sa, sb, dr);
}

int AlignUtil::dynamic(const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb, const double gap_penalty, std::vector<SAVE>& dr,
                       double (*sfunc)(const int&, const int&, void*), void* data)
{
       int m = sa.size();
       int n = sb.size();
       int up, lw;
       stripe(m, n, up, lw);

       RECD *dd = new RECD[n + 1];
       RECD *p  = new RECD[n + 1];
       RECD *q  = new RECD[n + 1];

       int k = adr(0, 0, -1, dr);
       for (int i = 0; i <= n; i++) {
            p[i].val = 0; p[i].ptr = k;
            q[i].val = 0; q[i].ptr = k;
            dd[i].val = 0; dd[i].ptr = k;
       }
       int j = 0;
       double x;
       for (int i = 1; i <= m; i++) {
            int n1 = i + lw + 1;
            int n2 = i + up;
            j = MAX(n1, 1);
            int n9 = MIN(n2, n);
            RECD *d = dd +j - 1;
            RECD *f = q + j - 1;
            RECD *g = p + j - 1;
            if (j == 1) {
               d->val = 0; d->ptr = k;
               f->val = 0; f->ptr = k;
            }
            RECD gg = *g;
            RECD ff = *f;
            RECD dt = *d;
            for (d++, g++, f++; j <= n9; d++, g++, f++, j++) {
                 RECD nd = ff;
                 if (gg.val > nd.val) nd = gg;
                 nd.val -= gap_penalty;
                 gg = *g;
                 ff = *f;
                 RECD tt = *d;
                 if ((d-1)->val >= (f-1)->val) {
                      f->val = (d-1)->val; f->ptr = (d-1)->ptr;
                 } else {
                      f->val = (f-1)->val; f->ptr = (f-1)->ptr;
                 }
                 if ((x = d->val) >= g->val) {
                      g->val = x; g->ptr = d->ptr;
                 }
                 d->val = dt.val;
                 if (nd.val > d->val) {
                      d->val = nd.val;
                      d->ptr = adr(i - 1, j - 1, nd.ptr, dr);
                 } else d->ptr = adr(i - 1, j - 1, dt.ptr, dr);
                 dt = tt;
                 d->val += (*sfunc)(sa[i-1][0], sb[j-1][0], data);
            }
       }
       x = dd[0].val;
       for (int i = 1; i <= n; i++)
            if (dd[i].val > x) {
                 x = dd[i].val;
                 j = dd[i].ptr;
            }
       for (int i = 1; i <= n; i++)
            if (p[i].val > x) {
                 x = p[i].val;
                 j = p[i].ptr;
            }
       for (int i = 1; i <= n; i++)
            if (q[i].val > x) {
                 x = q[i].val;
                 j = q[i].ptr;
            }

       delete [] dd;
       delete [] p;
       delete [] q;

       return(adr(m, n, j, dr));
}

int AlignUtil::dynamic(const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb, const double& vv, const double& uu,
                       std::vector<SAVE>& dr, double (*sfunc)(const int&, const int&, void*), void *data, const std::vector<int>& linkage,
                       const double& factor)
{
       int m = sa.size();
       int n = sb.size();

       RECD *dd = new RECD[n + 1];
       RECD *gg = new RECD[n + 1];
       char *dir = new char[m + n + 1];

       int origin = adr(0, 0, -1, dr);
       for (int i = 0; i < (m + n + 1); i++) dir[i] = 0;
       for (int i = 0; i <= n; i++) {
            dd[i].val = 0; dd[i].ptr = origin;
            gg[i].val = 0; gg[i].ptr = origin;
       }

       // double /* big_vv = vv;
       // if (!linkage.empty()) */ big_vv = 10 * vv;
       double big_vv = factor * vv;
       int k = 0;
       double x, max_val = 0, maximum = -1.0e38;
       RECD  nd, f, dt, dtt;
       for (int i = 0; i < m; i++) {
            int j  = 0;
            RECD *d = dd + j;
            RECD *g = gg + j;
            d->val = f.val = 0;
            d->ptr = f.ptr = origin;
            int r = j - i + m;
            dt = *d;
            for (d++, g++; j < n; d++, g++, r++, j++) {
                 if ((x = (d-1)->val - big_vv - uu) >= (f.val -= uu)) {
                      f.val = x; f.ptr = (d-1)->ptr;
                 }
                 double vv1 = vv;
                 if (!linkage.empty() && linkage[j]) vv1 = big_vv;
                 if ((x = d->val - vv1 - uu) >= (g->val -= uu)) {
                      g->val = x; g->ptr = d->ptr;
                 }
                 nd.val = maximum;
                 nd.ptr = -1;
                 if (f.val > nd.val) nd = f;
                 if (g->val > nd.val) nd = *g;
                 dt.val += (*sfunc)(sa[i][0], sb[j][0], data);
                 dtt = *d;
                 *d = dt;
                 if (nd.val > d->val) {
                      *d = nd;
                      dir[r] = 0;
                 } else if (!dir[r]) {
                      d->ptr = adr(i, j, d->ptr, dr);
                      dir[r] = 1;
                 }
                 if (d->val > max_val) {
                      max_val = d->val;
                      k = d->ptr;
                 }
                 dt = dtt;
            }
       }

       delete [] dd;
       delete [] gg;
       delete [] dir;

       return (adr(m, n, k, dr));
}

void AlignUtil::mu_trcback(const int& origin, std::vector<std::vector<int> >& ss, const std::vector<std::vector<int> >& a,
                           const std::vector<std::vector<int> >& b, const std::vector<SAVE>& dr)
{
       ss.clear();

       std::list<std::pair<int, int> > top;
       top.clear();

       int i = origin;
       while (i >= 0) {
            top.push_front(std::make_pair(dr[i].m, dr[i].n));
            i = dr[i].pp;
       }
       if (top.empty()) return;

       int n1 = 0;
       int n2 = 0;
       int j, m, n, r;
       std::list<std::pair<int, int> >::iterator pos = top.begin();
       std::list<std::pair<int, int> >::iterator pos1 = top.begin();
       pos1++;
       while (pos1 != top.end()) {
	    if ((i = pos->first) - (j = pos->second) > 
                (m = pos1->first) - (n = pos1->second) && 
                (r = m - i + j) != j) {
                 n1 += (n - r); 
                 top.insert(pos1, std::make_pair(m, r));
            } else if ((i = pos->first) - (j = pos->second) < 
               (m = pos1->first) - (n = pos1->second) && 
               (r = n + i - j) != i) {
                 n2 += (m - r); 
                 top.insert(pos1, std::make_pair(r, n));
            }
            pos = pos1;
            pos1++;
       }

       m = a.size() + n1;
       n = b.size() + n2;
       int n9 = MAX(m, n);
       ss.reserve(n9);
       std::vector<int> data;
       data.clear();
       data.push_back(-1);
       data.push_back(-1);
       for (i = 0; i < n9; ++i) ss.push_back(data);

       track(ss, top, a, b);
}

void AlignUtil::track(std::vector<std::vector<int> >& aa, std::list<std::pair<int, int> >& top,
                      const std::vector<std::vector<int> >& sa, const std::vector<std::vector<int> >& sb)
{
       int x, y, m, n, r;

       r = 0;
       std::list<std::pair<int, int> >::iterator pos = top.begin();
       std::list<std::pair<int, int> >::iterator pos1 = top.begin();
       pos1++;
       while (pos1 != top.end()) {
	    if ((x = pos->first) - (y = pos->second) == 
                (m = pos1->first) - (n = pos1->second)) {
		 for (int i = 0; i < m - x; ++i) {
                      aa[i + r][0] = sa[x + i][0];
                      aa[i + r][1] = sb[y + i][0];
		 }
		 r += (m - x);
	    } else if(x - y < m - n) {
		 for (int i = 0; i < m - x; ++i) {
                      aa[i + r][0] = sa[x + i][0];
		 }
		 r += (m - x);
	    } else {
		 for (int i = 0; i < n - y; ++i) {
                      aa[i + r][1] = sb[y + i][0];
		 }
		 r += (n - y);
	    }
            pos = pos1;
            pos1++;
       }
}

int AlignUtil::adr(const int& m, const int& n, const int& pp, std::vector<SAVE>& dr)
{
       int i_record = dr.size();

       SAVE s;
       s.m = m;
       s.n = n;
       s.pp = pp;
       dr.push_back(s);  

       return (i_record);
}

void AlignUtil::stripe(const int& a, const int& b, int& up, int& lw)
{
       int  p;

       up = b - a; lw = 0;
       if (up < lw) {p = up; up = lw; lw = p;}
       up += 25; lw -= 25;
       if ((p = b - 1) < up) up = p + 1;
       if ((p = 1 - a) > lw) lw = p - 1;
}
