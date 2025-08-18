// This is a port of Constrainautor.ts to work with the C++ port of Delaunator

#pragma once

#include <vector>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <bitset>
#include "delaunator.hpp"

namespace constrainautor {

inline int nextEdge(int e) { return (e % 3 == 2) ? e - 2 : e + 1; }
inline int prevEdge(int e) { return (e % 3 == 0) ? e + 2 : e - 1; }

// Use the same invalid index value as delaunator
constexpr std::size_t INVALID_INDEX = delaunator::INVALID_INDEX;

class Constrainautor {
public:
    delaunator::Delaunator& del;
    std::vector<uint32_t> vertMap;
    std::vector<bool> flips;
    std::vector<bool> consd;

    Constrainautor(delaunator::Delaunator& delaunator) 
        : del(delaunator),
          vertMap(del.coords.size() / 2, std::numeric_limits<uint32_t>::max()),
          flips(del.triangles.size(), false),
          consd(del.triangles.size(), false) {
        
        for (size_t e = 0; e < del.triangles.size(); e++) {
            const size_t v = del.triangles[e];
            if (vertMap[v] == std::numeric_limits<uint32_t>::max()) {
                updateVert(e);
            }
        }
    }

    // Constrain one edge between two points
    int constrainOne(size_t segP1, size_t segP2) {
        const auto& triangles = del.triangles;
        const auto& halfedges = del.halfedges;
        const size_t start = vertMap[segP1];
        
        // Loop over edges touching segP1
        size_t edg = start;
        do {
            const size_t p4 = triangles[edg];
            const size_t nxt = nextEdge(edg);
            
            // Already constrained in reverse order
            if (p4 == segP2) {
                return protect(edg);
            }

            const size_t opp = prevEdge(edg);
            const size_t p3 = triangles[opp];
            
            // Already constrained
            if (p3 == segP2) {
                protect(nxt);
                return nxt;
            }
            
            // Edge opposite segP1 intersects constraint
            if (intersectSegments(segP1, segP2, p3, p4)) {
                edg = opp;
                break;
            }
            
            const size_t adj = halfedges[nxt];
            edg = adj;
        } while (edg != INVALID_INDEX && edg != start);

        size_t conEdge = edg;
        size_t rescan = INVALID_INDEX;
        
        while (edg != INVALID_INDEX) {
            const size_t adj = halfedges[edg];
            const size_t bot = prevEdge(edg);
            const size_t top = prevEdge(adj);
            const size_t rgt = nextEdge(adj);
            
            if (adj == INVALID_INDEX) {
                throw std::runtime_error("Constraining edge exited the hull");
            }
            
            if (consd[edg]) {
                throw std::runtime_error("Edge intersects already constrained edge");
            }
            
            if (isCollinear(segP1, segP2, triangles[edg]) ||
                isCollinear(segP1, segP2, triangles[adj])) {
                throw std::runtime_error("Constraining edge intersects point");
            }
            
            const bool convex = intersectSegments(
                triangles[edg],
                triangles[adj],
                triangles[bot],
                triangles[top]
            );
            
            if (!convex) {
                if (rescan == INVALID_INDEX) {
                    rescan = edg;
                }
                
                if (triangles[top] == segP2) {
                    if (edg == rescan) {
                        throw std::runtime_error("Infinite loop: non-convex quadrilateral");
                    }
                    edg = rescan;
                    rescan = INVALID_INDEX;
                    continue;
                }
                
                if (intersectSegments(segP1, segP2, triangles[top], triangles[adj])) {
                    edg = top;
                } else if (intersectSegments(segP1, segP2, triangles[rgt], triangles[top])) {
                    edg = rgt;
                } else if (rescan == edg) {
                    throw std::runtime_error("Infinite loop: no further intersect after non-convex");
                }
                
                continue;
            }
            
            flipDiagonal(edg);
            
            if (intersectSegments(segP1, segP2, triangles[bot], triangles[top])) {
                if (rescan == INVALID_INDEX) {
                    rescan = bot;
                }
                if (rescan == bot) {
                    throw std::runtime_error("Infinite loop: flipped diagonal still intersects");
                }
            }
            
            if (triangles[top] == segP2) {
                conEdge = top;
                edg = rescan;
                rescan = INVALID_INDEX;
            } else if (intersectSegments(segP1, segP2, triangles[rgt], triangles[top])) {
                edg = rgt;
            }
        }
        
        protect(conEdge);
        
        bool anyFlips;
        do {
            anyFlips = false;
            for (size_t i = 0; i < flips.size(); i++) {
                if (flips[i]) {
                    flips[i] = false;
                    
                    const size_t adj = del.halfedges[i];
                    if (adj == INVALID_INDEX) continue;
                    
                    flips[adj] = false;
                    
                    if (!isDelaunay(i)) {
                        flipDiagonal(i);
                        anyFlips = true;
                    }
                }
            }
        } while (anyFlips);
        
        return findEdge(segP1, segP2);
    }

    /**
     * Fix the Delaunay condition. This ensures all triangles satisfy the
     * Delaunay property after constraining edges.
     *
     * @param deep If true, keep checking & flipping edges until all
     *        edges are Delaunay, otherwise only check the edges once.
     * @return Reference to this object for method chaining.
     */
    Constrainautor& delaunify(bool deep = false) {
        const auto& halfedges = del.halfedges;
        const size_t len = halfedges.size();
        
        do {
            int flipped = 0;
            for (size_t edg = 0; edg < len; edg++) {
                if (consd[edg]) {
                    continue;
                }
                flips[edg] = false;
                
                const size_t adj = halfedges[edg];
                if (adj == INVALID_INDEX) {
                    continue;
                }
                
                flips[adj] = false;
                if (!isDelaunay(edg)) {
                    flipDiagonal(edg);
                    flipped++;
                }
            }
            
            if (!deep || flipped == 0) break;
        } while (true);
        
        return *this;
    }

    /**
     * Call constrainOne on each edge, and delaunify afterwards.
     *
     * @param edges Vector of edges to constrain: each element is a pair [p1, p2]
     *        which are indices into the points array originally supplied to Delaunator.
     * @return Reference to this object for method chaining.
     */
    Constrainautor& constrainAll(const std::vector<std::pair<size_t, size_t>>& edges) {
        for (const auto& edge : edges) {
            constrainOne(edge.first, edge.second);
        }
        
        return *this;
    }

    /**
     * Whether an edge is a constrained edge.
     *
     * @param edg The edge id.
     * @return True if the edge is constrained.
     */
    bool isConstrained(size_t edg) const {
        return consd[edg];
    }

    /**
     * Find the edge that points from p1 -> p2. If there is only an edge from
     * p2 -> p1 (i.e. it is on the hull), returns the negative id of it.
     * 
     * @param p1 The index of the first point into the points array.
     * @param p2 The index of the second point into the points array.
     * @return The id of the edge that points from p1 -> p2, or the negative
     *         id of the edge that goes from p2 -> p1, or max int if there is
     *         no edge between p1 and p2.
     */
    int findEdge(size_t p1, size_t p2) {
        const size_t start1 = vertMap[p2];
        size_t edg = start1;
        size_t prv = INVALID_INDEX;
        
        do {
            if (del.triangles[edg] == p1) {
                return edg;
            }
            prv = nextEdge(edg);
            edg = del.halfedges[prv];
        } while (edg != INVALID_INDEX && edg != start1);

        if (del.triangles[nextEdge(prv)] == p1) {
            return -static_cast<int>(prv);
        }

        return std::numeric_limits<int>::max();
    }

protected:
    bool intersectSegments(size_t p1, size_t p2, size_t p3, size_t p4) {
        if (p1 == p3 || p1 == p4 || p2 == p3 || p2 == p4) {
            return false;
        }
        
        const double p1x = del.coords[p1 * 2];
        const double p1y = del.coords[p1 * 2 + 1];
        const double p2x = del.coords[p2 * 2];
        const double p2y = del.coords[p2 * 2 + 1];
        const double p3x = del.coords[p3 * 2];
        const double p3y = del.coords[p3 * 2 + 1];
        const double p4x = del.coords[p4 * 2];
        const double p4y = del.coords[p4 * 2 + 1];

        return intersectSegments(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y);
    }

    static bool intersectSegments(
        double p1x, double p1y, double p2x, double p2y,
        double p3x, double p3y, double p4x, double p4y) {
        
        const double x0 = orient2d(p1x, p1y, p3x, p3y, p4x, p4y);
        const double y0 = orient2d(p2x, p2y, p3x, p3y, p4x, p4y);
        
        if ((x0 > 0 && y0 > 0) || (x0 < 0 && y0 < 0)) {
            return false;
        }

        const double x1 = orient2d(p3x, p3y, p1x, p1y, p2x, p2y);
        const double y1 = orient2d(p4x, p4y, p1x, p1y, p2x, p2y);
        
        if ((x1 > 0 && y1 > 0) || (x1 < 0 && y1 < 0)) {
            return false;
        }

        if (x0 == 0 && y0 == 0 && x1 == 0 && y1 == 0) {
            return !(std::max(p3x, p4x) < std::min(p1x, p2x) ||
                    std::max(p1x, p2x) < std::min(p3x, p4x) ||
                    std::max(p3y, p4y) < std::min(p1y, p2y) ||
                    std::max(p1y, p2y) < std::min(p3y, p4y));
        }

        return true;
    }

    static double orient2d(double ax, double ay, double bx, double by, double cx, double cy) {
        return (by - ay) * (cx - bx) - (bx - ax) * (cy - by);
    }

    bool isCollinear(size_t p1, size_t p2, size_t p) {
        return orient2d(
            del.coords[p1 * 2], del.coords[p1 * 2 + 1],
            del.coords[p2 * 2], del.coords[p2 * 2 + 1],
            del.coords[p * 2], del.coords[p * 2 + 1]
        ) == 0.0;
    }

    bool inCircle(size_t p1, size_t p2, size_t p3, size_t px) {
        return delaunator::in_circle(
            del.coords[p1 * 2], del.coords[p1 * 2 + 1],
            del.coords[p2 * 2], del.coords[p2 * 2 + 1], 
            del.coords[p3 * 2], del.coords[p3 * 2 + 1],
            del.coords[px * 2], del.coords[px * 2 + 1]
        );
    }

private:
    int protect(size_t edg) {
        const size_t adj = del.halfedges[edg];
        flips[edg] = false;
        consd[edg] = true;
        
        if (adj != INVALID_INDEX) {
            flips[adj] = false;
            consd[adj] = true;
            return static_cast<int>(adj);
        }
        
        return -static_cast<int>(edg);
    }

    bool markFlip(size_t edg) {
        if (consd[edg]) {
            return false;
        }
        
        const size_t adj = del.halfedges[edg];
        if (adj != INVALID_INDEX) {
            flips[edg] = true;
            flips[adj] = true;
        }
        return true;
    }

    size_t flipDiagonal(size_t edg) {
        const size_t adj = del.halfedges[edg];
        const size_t bot = prevEdge(edg);
        const size_t lft = nextEdge(edg);
        const size_t top = prevEdge(adj);
        const size_t rgt = nextEdge(adj);
        const size_t adjBot = del.halfedges[bot];
        const size_t adjTop = del.halfedges[top];

        if (consd[edg]) {
            throw std::runtime_error("Trying to flip a constrained edge");
        }

        // Move *edg to *top
        del.triangles[edg] = del.triangles[top];
        del.halfedges[edg] = adjTop;
        if (!flips[edg]) {
            consd[edg] = consd[top];
        }
        if (adjTop != INVALID_INDEX) {
            del.halfedges[adjTop] = edg;
        }
        del.halfedges[bot] = top;

        // Move *adj to *bot
        del.triangles[adj] = del.triangles[bot];
        del.halfedges[adj] = adjBot;
        if (!flips[adj]) {
            consd[adj] = consd[bot];
        }
        if (adjBot != INVALID_INDEX) {
            del.halfedges[adjBot] = adj;
        }
        del.halfedges[top] = bot;

        markFlip(edg);
        markFlip(lft);
        markFlip(adj);
        markFlip(rgt);

        flips[bot] = true;
        consd[bot] = false;
        flips[top] = true;
        consd[top] = false;

        updateVert(edg);
        updateVert(lft);
        updateVert(adj);
        updateVert(rgt);

        return bot;
    }

    bool isDelaunay(size_t edg) {
        const size_t adj = del.halfedges[edg];
        if (adj == INVALID_INDEX) {
            return true;
        }

        const size_t p1 = del.triangles[prevEdge(edg)];
        const size_t p2 = del.triangles[edg];
        const size_t p3 = del.triangles[nextEdge(edg)];
        const size_t px = del.triangles[prevEdge(adj)];

        return !inCircle(p1, p2, p3, px);
    }

    size_t updateVert(size_t start) {
        const size_t v = del.triangles[start];
        size_t inc = prevEdge(start);
        size_t adj = del.halfedges[inc];
        
        while (adj != INVALID_INDEX && adj != start) {
            inc = prevEdge(adj);
            adj = del.halfedges[inc];
        }
        
        vertMap[v] = inc;
        return inc;
    }
};

} // namespace constrainautor