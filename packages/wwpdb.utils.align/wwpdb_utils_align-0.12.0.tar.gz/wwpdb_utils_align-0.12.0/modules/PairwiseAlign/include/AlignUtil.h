/*$$FILE$$*/
/*$$VERSION$$*/
/*$$DATE$$*/
/*$$LICENSE$*/
#ifndef _ALIGN_UTIL_H_
#define _ALIGN_UTIL_H_

#include <list>
#include <vector>

class AlignUtil
{
  public:
       static void initAssignment(std::vector<std::vector<int> >& ss, const int& size);
       static void Alignment(std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&,
                             const double&, double (*)(const int&, const int&, void*), void*);
       static void Alignment(std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const double&,
                             const double&, double (*)(const int&, const int&, void*), void*, const std::vector<int>& linkage = std::vector<int>(),
                             const double& factor = 10);
  private:
       typedef struct {
               int  m,  n;
               int  pp;
       } SAVE;
       
       typedef struct {
               double val;
               int    ptr;
       } RECD;

       static int dynamic(const std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const double, std::vector<SAVE>&,
                          double (*)(const int&, const int&, void*), void*);
       static int dynamic(const std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const double&, const double&, std::vector<SAVE>&,
                          double (*)(const int&, const int&, void*), void*, const std::vector<int>&, const double& factor = 10);
       static void mu_trcback(const int&, std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&, const std::vector<std::vector<int> >&,
                              const std::vector<SAVE>&); 
       static void track(std::vector<std::vector<int> >&, std::list<std::pair<int, int> >&, const std::vector<std::vector<int> >&,
                         const std::vector<std::vector<int> >&); 
       static int adr(const int&, const int&, const int&, std::vector<SAVE>&);
       static void stripe(const int&, const int&, int&, int&);
};

#endif
